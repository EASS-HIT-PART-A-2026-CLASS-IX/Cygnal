import os

import httpx


BASE_URL = os.getenv("CYGNAL_API_URL", "http://127.0.0.1:8000").rstrip("/")

SAMPLE_INDICATORS = [
    {
        "indicator_type": "IP",
        "value": "203.0.113.42",
        "severity": "critical",
        "source": "Demo-OSINT",
        "confidence": 96,
        "tags": ["demo", "c2", "scanner"],
        "threat_actor": "Demo-Campaign-Red",
        "is_active": True,
    },
    {
        "indicator_type": "IP",
        "value": "198.51.100.77",
        "severity": "medium",
        "source": "Internal-SOC",
        "confidence": 68,
        "tags": ["demo", "brute-force"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "Domain",
        "value": "c2-beacon.example",
        "severity": "critical",
        "source": "Demo-OSINT",
        "confidence": 94,
        "tags": ["demo", "c2", "ransomware"],
        "threat_actor": "Demo-Ransomware",
        "is_active": True,
    },
    {
        "indicator_type": "Domain",
        "value": "credential-update.example",
        "severity": "high",
        "source": "Phishing-Lab",
        "confidence": 91,
        "tags": ["demo", "phishing", "credential-theft"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "URL",
        "value": "https://credential-update.example/verify",
        "severity": "high",
        "source": "Phishing-Lab",
        "confidence": 89,
        "tags": ["demo", "phishing"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "URL",
        "value": "http://payload-download.example/update.exe",
        "severity": "critical",
        "source": "Sandbox",
        "confidence": 97,
        "tags": ["demo", "malware", "payload"],
        "threat_actor": "Demo-Campaign-Red",
        "is_active": True,
    },
    {
        "indicator_type": "Hash",
        "value": "d41d8cd98f00b204e9800998ecf8427e",
        "severity": "high",
        "source": "Sandbox",
        "confidence": 82,
        "tags": ["demo", "malware", "md5"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "Hash",
        "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "severity": "medium",
        "source": "Malware-Lab",
        "confidence": 75,
        "tags": ["demo", "sha256"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "Email",
        "value": "billing@credential-update.example",
        "severity": "medium",
        "source": "Mail-Gateway",
        "confidence": 78,
        "tags": ["demo", "phishing", "invoice"],
        "threat_actor": None,
        "is_active": True,
    },
    {
        "indicator_type": "Email",
        "value": "alerts@c2-beacon.example",
        "severity": "low",
        "source": "Internal-SOC",
        "confidence": 55,
        "tags": ["demo", "suspicious-sender"],
        "threat_actor": None,
        "is_active": False,
    },
]


def seed() -> tuple[int, int]:
    """Add safe demonstration IOCs once and return added/skipped counts."""
    print(f"Seeding Cygnal at {BASE_URL} with demonstration indicators...\n")
    added = 0
    skipped = 0
    try:
        with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
            response = client.get("/indicators", params={"limit": 100})
            response.raise_for_status()
            existing = {(item["indicator_type"], item["value"]) for item in response.json()}

            for indicator in SAMPLE_INDICATORS:
                key = (indicator["indicator_type"], indicator["value"])
                if key in existing:
                    skipped += 1
                    print(f"   SKIP [{key[0]}] {key[1]}")
                    continue
                response = client.post("/indicators", json=indicator)
                response.raise_for_status()
                data = response.json()
                existing.add(key)
                added += 1
                print(f"   ADD  [{data['indicator_type']}] {data['value']} (id={data['id']})")
    except httpx.HTTPError as exc:
        print(f"   ERROR: Could not seed the API: {exc}")
        return added, skipped

    print(f"\nDone: {added} added, {skipped} already present.")
    return added, skipped


if __name__ == "__main__":
    seed()
