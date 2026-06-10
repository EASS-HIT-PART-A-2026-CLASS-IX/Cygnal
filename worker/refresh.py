import asyncio
import hashlib
import logging
import uuid

import httpx
import redis.asyncio as aioredis
from sqlmodel import Session, create_engine

from backend.models.indicator import Indicator
from backend.schemas.indicators import IndicatorCreate
from worker.config import settings


logger = logging.getLogger(__name__)
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)


def ioc_fingerprint(value: str, indicator_type: str) -> str:
    return hashlib.sha256(f"{indicator_type}:{value}".encode()).hexdigest()


async def fetch_abusive_ips(limit: int = 10, attempts: int | None = None) -> list[dict]:
    attempts = attempts or settings.refresh_max_attempts
    if not settings.abuseipdb_api_key:
        return [
            {"ipAddress": "185.220.101.45", "abuseConfidenceScore": 95, "countryCode": "DE"},
            {"ipAddress": "45.142.212.100", "abuseConfidenceScore": 88, "countryCode": "RU"},
            {"ipAddress": "192.42.116.16", "abuseConfidenceScore": 72, "countryCode": "NL"},
        ]
    for attempt in range(1, attempts + 1):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.abuseipdb.com/api/v2/blacklist",
                    headers={"Key": settings.abuseipdb_api_key, "Accept": "application/json"},
                    params={"confidenceMinimum": 70, "limit": limit},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json().get("data", [])
        except httpx.HTTPError:
            if attempt == attempts:
                raise
            await asyncio.sleep(0.5 * (2 ** (attempt - 1)))
    raise RuntimeError("AbuseIPDB refresh exhausted without a response")


async def process_entry(entry: dict, redis_client: aioredis.Redis) -> str:
    ip = entry["ipAddress"]
    confidence = entry["abuseConfidenceScore"]
    redis_key = f"ioc:seen:{ioc_fingerprint(ip, 'IP')}"
    trace_id = str(uuid.uuid4())
    claimed = await redis_client.set(redis_key, "1", ex=settings.idempotency_ttl_seconds, nx=True)
    if not claimed:
        logger.info("trace_id=%s idempotency_key=%s result=skipped", trace_id, redis_key)
        return "skipped"
    try:
        indicator = Indicator.model_validate(
            IndicatorCreate(
                indicator_type="IP",
                value=ip,
                severity="high" if confidence >= 90 else "medium",
                source="AbuseIPDB",
                confidence=confidence,
                tags=["auto-imported", "abuseipdb"],
            )
        )
        with Session(engine) as session:
            session.add(indicator)
            session.commit()
        logger.info("trace_id=%s idempotency_key=%s result=added", trace_id, redis_key)
        return "added"
    except Exception:
        await redis_client.delete(redis_key)
        raise


async def refresh(redis_client: aioredis.Redis, max_concurrency: int | None = None) -> tuple[int, int]:
    semaphore = asyncio.Semaphore(max_concurrency or settings.refresh_max_concurrency)

    async def bounded_process(entry: dict) -> str:
        async with semaphore:
            return await process_entry(entry, redis_client)

    results = await asyncio.gather(*(bounded_process(entry) for entry in await fetch_abusive_ips()))
    return results.count("added"), results.count("skipped")


async def run() -> tuple[int, int]:
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    try:
        return await refresh(redis_client)
    finally:
        await redis_client.aclose()
