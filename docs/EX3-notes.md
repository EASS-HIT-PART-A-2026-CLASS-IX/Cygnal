# 📋 EX3 – Architecture Notes & Decisions

## 🏗️ Services Overview

| Service | Technology | Port | Role |
|---------|-----------|------|------|
| `api` | FastAPI + SQLModel | 8000 | Core backend, CRUD for IOCs |
| `dashboard` | Streamlit | 8501 | Visual interface for analysts |
| `worker` | Python + httpx | — | Auto-imports IOCs from AbuseIPDB |
| `redis` | Redis 7 Alpine | 6379 | Idempotency tracking + rate limiting |

---

## 🔄 Worker & Idempotency

The `scripts/refresh.py` worker pulls malicious IPs from **AbuseIPDB** and stores them in the database.

To prevent duplicate imports, every IOC is fingerprinted with SHA-256:

```text
fingerprint = sha256("IP:185.220.101.45")
```

The fingerprint is stored in Redis with a **24-hour TTL**:

```text
ioc:seen:<fingerprint> = "1"  (expires in 86400s)
```

If the key exists → skip. If not → insert + mark in Redis.

---

## 🤖 AI Analyst Microservice

The `ai_analyst` service uses the **Claude API (Anthropic)** to:
- Analyze a single IOC and return a threat assessment
- Generate a summary report of all active IOCs

---

## 🔒 Security Baseline

- Hashed credentials with `bcrypt`
- JWT-protected routes with role checks (`analyst` / `admin`)
- Token expiry and rotation documented below

### JWT Flow
1. `POST /auth/login` → returns `access_token`
2. Include header: `Authorization: Bearer <token>`
3. Protected routes check role claim in token payload

---

## 📊 Enhancement – IOC Summary Report

One-click **CSV export** and **AI-generated summary** available from the Streamlit dashboard.

---

## 🔍 Redis Trace

Example Redis keys after a refresh run:

```text
ioc:seen:a3f2c1... (TTL: 86234s)
ioc:seen:b7d4e2... (TTL: 85901s)
rate:127.0.0.1:/indicators (TTL: 47s)
```

---

## 🤖 AI Assistance

This project was developed with the assistance of **Claude (Anthropic)**.
All AI-generated code was reviewed, understood, and verified locally before being committed.