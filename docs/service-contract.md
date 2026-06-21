# Cygnal Service Contract

## Shared API Headers

Every backend response includes:

- `X-Trace-Id`;
- `X-RateLimit-Limit`;
- `X-RateLimit-Remaining`.

Rate-limit rejection returns `429` and `Retry-After: 60`. Errors use a shared
status/error/detail/trace envelope.

## Indicator Validation

`POST /indicators` rejects undeclared fields and validates the value according to
`indicator_type`:

- IP: valid IPv4 or IPv6;
- Domain: normalized DNS domain;
- URL: HTTP or HTTPS URL with a hostname;
- Hash: hexadecimal MD5, SHA-1, SHA-256, or SHA-512;
- Email: address-shaped local and domain parts.

Confidence is limited to 0-100, and type/severity use enums.

## Listing and Pagination

`GET /indicators` returns an ID-ordered array and supports `skip`, `limit`,
`indicator_type`, `severity`, and `is_active`.

`GET /indicators/page` returns:

```json
{
  "page": 1,
  "page_size": 20,
  "total": 1,
  "items": []
}
```

It includes `X-Total-Count` and a weak `ETag`. Repeating the request with a
matching `If-None-Match` returns `304 Not Modified`.

## CSV Export

`GET /indicators/export.csv` returns this deterministic column order:

```text
id,indicator_type,value,severity,source,confidence,tags,threat_actor,is_active,created_at
```

The JSON listing filters are also available for CSV.

## Authentication and Mutation

`POST /auth/login` accepts form-encoded credentials. JWTs contain expiration,
issued-at, issuer, audience, subject, and role claims.

- Create and update use validated request schemas.
- Delete requires an authenticated user.
- Deactivate requires the `admin` role.

## Enrichment Service

The enrichment service is exposed separately on port 8001.

`POST /analyze` request:

```json
{"indicator_id": 1}
```

The response contains `risk_score`, `risk_level`, `confidence`, `summary`,
`reasoning`, `recommended_actions`, `type_analysis`, `source_context`,
`historical_context`, `analysis_mode`, and an optional local-model explanation.

`POST /report` returns deterministic aggregate risk metrics and a Markdown
summary. Both endpoints work without a paid API key.
