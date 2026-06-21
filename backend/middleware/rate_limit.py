import time

import redis.asyncio as aioredis
from fastapi import Request
from redis.exceptions import RedisError

from backend.core.config import settings


async def check_rate_limit(request: Request) -> tuple[bool, int]:
    client_host = request.client.host if request.client else "unknown"
    key = f"rate:{client_host}:{request.url.path}:{int(time.time() // 60)}"
    redis_client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )
    try:
        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, 60)
        remaining = max(settings.rate_limit_per_minute - current, 0)
        return current <= settings.rate_limit_per_minute, remaining
    except RedisError:
        return True, settings.rate_limit_per_minute
    finally:
        await redis_client.aclose()
