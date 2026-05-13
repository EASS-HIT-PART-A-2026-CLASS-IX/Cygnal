"""
refresh.py – pulls fresh IOCs from AbuseIPDB and stores them with Redis-backed idempotency.
Run with: uv run python scripts/refresh.py
"""

import asyncio
import hashlib
import os
import httpx
import redis.asyncio as aioredis
from sqlmodel import Session, create_engine
from backend.models import Indicator, IndicatorCreate

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///cygnal.db")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
ABUSEIPDB_API_KEY = os.getenv("ABUSEIPDB_API_KEY", "")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def ioc_fingerprint(value: str, indicator_type: str) -> str:
    """צור מזהה ייחודי לכל IOC כדי למנוע כפילויות."""
    return hashlib.sha256(f"{indicator_type}:{value}".encode()).hexdigest()


async def fetch_abusive_ips(limit: int = 10) -> list[dict]:
    """שלוף IPs זדוניות מ-AbuseIPDB."""
    if not ABUSEIPDB_API_KEY:
        print("⚠️  No ABUSEIPDB_API_KEY set – using mock data.")
        return [
            {"ipAddress": "185.220.101.45", "abuseConfidenceScore": 95, "countryCode": "DE"},
            {"ipAddress": "45.142.212.100", "abuseConfidenceScore": 88, "countryCode": "RU"},
            {"ipAddress": "192.42.116.16",  "abuseConfidenceScore": 72, "countryCode": "NL"},
        ]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.abuseipdb.com/api/v2/blacklist",
            headers={"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"},
            params={"confidenceMinimum": 70, "limit": limit},
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json().get("data", [])


async def refresh(redis_client: aioredis.Redis) -> None:
    print("🔄 Starting IOC refresh from AbuseIPDB...")
    ips = await fetch_abusive_ips()
    added = 0
    skipped = 0

    with Session(engine) as session:
        for entry in ips:
            ip = entry["ipAddress"]
            confidence = entry["abuseConfidenceScore"]
            fingerprint = ioc_fingerprint(ip, "IP")
            redis_key = f"ioc:seen:{fingerprint}"

            # Redis idempotency check – אם כבר ראינו את זה, נדלג
            already_seen = await redis_client.get(redis_key)
            if already_seen:
                skipped += 1
                continue

            indicator = Indicator.model_validate(IndicatorCreate(
                indicator_type="IP",
                value=ip,
                severity="high" if confidence >= 90 else "medium",
                source="AbuseIPDB",
                confidence=confidence,
                tags=["auto-imported", "abuseipdb"],
                threat_actor=None,
                is_active=True,
            ))
            session.add(indicator)
            session.commit()

            # סמן ב-Redis למשך 24 שעות
            await redis_client.setex(redis_key, 86400, "1")
            added += 1
            print(f"  ✅ Added [{indicator.severity.upper()}] {ip} (confidence={confidence})")

    print(f"\n✅ Refresh complete: {added} added, {skipped} skipped (already seen).")


async def main():
    redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)
    try:
        await refresh(redis_client)
    finally:
        await redis_client.aclose()


if __name__ == "__main__":
    asyncio.run(main())