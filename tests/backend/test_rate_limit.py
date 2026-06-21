from unittest.mock import AsyncMock, MagicMock

import pytest
from redis.exceptions import RedisError
from starlette.requests import Request

from backend.core.config import settings
from backend.middleware.rate_limit import check_rate_limit


@pytest.mark.anyio
async def test_rate_limit_uses_bounded_redis_timeouts(monkeypatch):
    redis_client = MagicMock()
    redis_client.incr = AsyncMock(side_effect=RedisError("offline"))
    redis_client.aclose = AsyncMock()
    from_url = MagicMock(return_value=redis_client)
    monkeypatch.setattr("backend.middleware.rate_limit.aioredis.from_url", from_url)
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/health",
            "headers": [],
            "query_string": b"",
            "scheme": "http",
            "server": ("testserver", 80),
            "client": ("testclient", 123),
        }
    )

    allowed, remaining = await check_rate_limit(request)

    assert allowed is True
    assert remaining == settings.rate_limit_per_minute
    from_url.assert_called_once_with(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=0.5,
        socket_timeout=0.5,
    )
    redis_client.aclose.assert_awaited_once()
