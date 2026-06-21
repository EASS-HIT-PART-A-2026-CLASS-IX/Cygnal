from __future__ import annotations

from ipaddress import ip_address
import re
from urllib.parse import urlparse

from backend.models.enums import IndicatorType


DOMAIN_PATTERN = re.compile(r"^(?=.{1,253}$)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$")
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
HASH_LENGTHS = {32: "MD5", 40: "SHA-1", 64: "SHA-256", 128: "SHA-512"}


def validate_ioc_value(indicator_type: IndicatorType | str, value: str) -> str:
    normalized = value.strip()
    kind = indicator_type.value if isinstance(indicator_type, IndicatorType) else str(indicator_type)

    if kind == IndicatorType.IP.value:
        try:
            return str(ip_address(normalized))
        except ValueError as exc:
            raise ValueError("must be a valid IPv4 or IPv6 address") from exc

    if kind == IndicatorType.DOMAIN.value:
        domain = normalized.rstrip(".").lower()
        if not DOMAIN_PATTERN.fullmatch(domain):
            raise ValueError("must be a valid domain name")
        return domain

    if kind == IndicatorType.URL.value:
        parsed = urlparse(normalized)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("must be a valid HTTP or HTTPS URL")
        return normalized

    if kind == IndicatorType.HASH.value:
        if len(normalized) not in HASH_LENGTHS or not re.fullmatch(r"[A-Fa-f0-9]+", normalized):
            raise ValueError("must be a hexadecimal MD5, SHA-1, SHA-256, or SHA-512 hash")
        return normalized.lower()

    if kind == IndicatorType.EMAIL.value:
        if not EMAIL_PATTERN.fullmatch(normalized):
            raise ValueError("must be a valid email address")
        return normalized.lower()

    raise ValueError("unsupported indicator type")
