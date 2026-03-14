import hashlib


def generate_record_hash(title: str, url: str) -> str:
    raw_value = f"{title.strip()}::{url.strip()}"
    return hashlib.sha256(raw_value.encode("utf-8")).hexdigest()