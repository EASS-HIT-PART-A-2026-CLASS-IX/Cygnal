import asyncio
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from worker import refresh as worker


@pytest.mark.anyio
async def test_refresh_uses_bounded_concurrency(monkeypatch):
    entries = [{"ipAddress": f"192.0.2.{index}", "abuseConfidenceScore": 80} for index in range(6)]
    active = 0
    peak = 0

    async def fake_fetch():
        return entries

    async def fake_process(entry, redis_client):
        nonlocal active, peak
        active += 1
        peak = max(peak, active)
        await asyncio.sleep(0.01)
        active -= 1
        return "added"

    monkeypatch.setattr(worker, "fetch_abusive_ips", fake_fetch)
    monkeypatch.setattr(worker, "process_entry", fake_process)

    added, skipped = await worker.refresh(MagicMock(), max_concurrency=2)

    assert (added, skipped) == (6, 0)
    assert peak == 2


@pytest.mark.anyio
async def test_process_entry_uses_atomic_redis_claim(monkeypatch, caplog):
    redis_client = MagicMock()
    redis_client.set = AsyncMock(return_value=False)
    session = MagicMock()
    session.__enter__.return_value = session
    session.__exit__.return_value = False
    monkeypatch.setattr(worker, "Session", MagicMock(return_value=session))

    with caplog.at_level("INFO"):
        result = await worker.process_entry(
            {"ipAddress": "192.0.2.1", "abuseConfidenceScore": 90},
            redis_client,
        )

    assert result == "skipped"
    redis_client.set.assert_awaited_once()
    assert redis_client.set.await_args.kwargs == {
        "ex": worker.settings.idempotency_ttl_seconds,
        "nx": True,
    }
    session.add.assert_not_called()
    assert "trace_id=" in caplog.text
    assert "idempotency_key=ioc:seen:" in caplog.text
    assert "result=skipped" in caplog.text


@pytest.mark.anyio
async def test_fetch_abusive_ips_retries_http_errors(monkeypatch):
    monkeypatch.setattr(worker.settings, "abuseipdb_api_key", "test-key")
    response = MagicMock()
    response.raise_for_status.side_effect = [
        httpx.HTTPStatusError("temporary", request=MagicMock(), response=MagicMock()),
        None,
    ]
    response.json.return_value = {"data": [{"ipAddress": "192.0.2.1"}]}
    client = AsyncMock()
    client.get.return_value = response
    client.__aenter__.return_value = client
    client.__aexit__.return_value = False
    monkeypatch.setattr(worker.httpx, "AsyncClient", MagicMock(return_value=client))
    monkeypatch.setattr(worker.asyncio, "sleep", AsyncMock())

    result = await worker.fetch_abusive_ips(attempts=2)

    assert result == [{"ipAddress": "192.0.2.1"}]
    assert client.get.await_count == 2
