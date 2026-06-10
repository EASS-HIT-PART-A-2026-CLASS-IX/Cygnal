# Cygnal Service Contract

## Shared Headers

Every API response includes:

- `X-Trace-Id`: accepts a caller-provided value or generates one.
- `X-RateLimit-Limit`: maximum requests per minute.
- `X-RateLimit-Remaining`: requests remaining in the current Redis-backed window.

When the limit is exceeded, the API returns `429` with `Retry-After: 60`.

All errors use the shared envelope:

```json
{
  "status": 404,
  "error": "resource_not_found",
  "detail": "Indicator not found",
  "trace_id": "caller-or-generated-trace-id"
}
```

## Indicator Listing

`GET /indicators` returns a deterministic ID-ordered JSON array. It accepts `skip`,
`limit`, `indicator_type`, `severity`, and `is_active` filters.

`GET /indicators/page` is the release-contract listing endpoint. It returns:

```json
{
  "page": 1,
  "page_size": 20,
  "total": 1,
  "items": []
}
```

The endpoint accepts `page` from 1 and `page_size` from 1 to 100. Responses include
`X-Total-Count` and a weak `ETag`. Repeating the request with the same value in
`If-None-Match` returns `304 Not Modified`.

## CSV Export

`GET /indicators/export.csv` returns ID-ordered indicators with this header order:

```text
id,indicator_type,value,severity,source,confidence,tags,threat_actor,is_active,created_at
```

Multiple tags are joined with commas and quoted according to standard CSV rules.
The same type, severity, and active-state filters supported by the JSON endpoints
are available for CSV export.

## Authentication

`POST /auth/login` accepts form-encoded `username` and `password`. Protected routes
require `Authorization: Bearer <token>`. Tokens include expiration, issued-at,
issuer, audience, subject, and role claims.

## Indicator Mutation

Create and update requests reject undeclared fields. Creation timestamps are
server-owned and cannot be supplied by API clients.
