"""
Seed script – populates Cygnal with sample threat indicators.
Run with: uv run python seed.py
"""

import httpx

BASE_URL = "http://127.0.0.1:8000"

SAMPLE_INDICATORS = [
    {
        "indicator_type": "IP",
        "value": "185.220.101.45",
        "severity": "critical",
        "source": "AbuseIPDB",
        "confidence": 95,
        "tags": ["tor-exit-node", "scanning"],
        "threat_actor": "Unknown",
        "is_active": True
    },
    {
        "indicator_type": "Domain",
        "value": "malware-c2.ru",
        "severity": "high",
        "source": "URLhaus",
        "confidence": 88,
        "tags": ["c2", "ransomware"],
        "threat_actor": "LockBit",
        "is_active": True
    },
    {
        "indicator_type": "URL",
        "value": "http://phishing-login.tk/paypal/verify",
        "severity": "high",
        "source": "PhishTank",
        "confidence": 92,
        "tags": ["phishing", "credential-theft"],
        "threat_actor": None,
        "is_active": True
    },
    {
        "indicator_type": "Hash",
        "value": "d41d8cd98f00b204e9800998ecf8427e",
        "severity": "critical",
        "source": "VirusTotal",
        "confidence": 99,
        "tags": ["malware", "ransomware", "APT29"],
        "threat_actor": "APT29",
        "is_active": True
    },
    {
        "indicator_type": "Email",
        "value": "phisher@spoofed-domain.com",
        "severity": "medium",
        "source": "Sentinel-Internal",
        "confidence": 70,
        "tags": ["phishing", "spear-phishing"],
        "threat_actor": None,
        "is_active": True
    },
]


def seed():
    print("🌱 Seeding Cygnal with sample indicators...\n")
    for indicator in SAMPLE_INDICATORS:
        response = httpx.post(f"{BASE_URL}/indicators", json=indicator)
        if response.status_code == 201:
            data = response.json()
            print(f"  ✅ [{data['indicator_type']}] {data['value']} (id={data['id']})")
        else:
            print(f"  ❌ Failed: {indicator['value']} → {response.status_code}")
    print(f"\n✅ Done! {len(SAMPLE_INDICATORS)} indicators seeded.")


if __name__ == "__main__":
    seed()