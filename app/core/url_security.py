import ipaddress
import socket
from urllib.parse import urlparse


BLOCKED_HOSTNAMES = {
    "localhost",
    "0.0.0.0",
}

BLOCKED_HOSTNAME_SUFFIXES = (
    ".local",
    ".internal",
    ".localhost",
)


class URLSecurityError(ValueError):
    pass


def _parse_url(url: str):
    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        raise URLSecurityError("URL must use http or https")

    if not parsed.hostname:
        raise URLSecurityError("URL must include a valid hostname")

    return parsed


def _validate_hostname(hostname: str) -> None:
    normalized_hostname = hostname.strip().lower()

    if not normalized_hostname:
        raise URLSecurityError("URL must include a valid hostname")

    if normalized_hostname in BLOCKED_HOSTNAMES:
        raise URLSecurityError("URL hostname is not allowed")

    if normalized_hostname.endswith(BLOCKED_HOSTNAME_SUFFIXES):
        raise URLSecurityError("URL hostname is not allowed")

    try:
        ip = ipaddress.ip_address(normalized_hostname)
    except ValueError:
        if "." not in normalized_hostname:
            raise URLSecurityError("URL hostname is not allowed")
        return

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_unspecified
        or ip.is_reserved
    ):
        raise URLSecurityError("URL hostname is not allowed")


def validate_source_url(value: str) -> str:
    parsed = _parse_url(value)
    _validate_hostname(parsed.hostname or "")
    return value


def assert_safe_outbound_url(url: str) -> str:
    parsed = _parse_url(url)
    hostname = parsed.hostname or ""
    _validate_hostname(hostname)

    try:
        address_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as exc:
        raise URLSecurityError("URL hostname could not be resolved") from exc

    for item in address_info:
        resolved_ip = item[4][0]
        _validate_hostname(resolved_ip)

    return url
