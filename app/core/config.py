import os


def get_env(name: str, default: str | None = None, *, required: bool = False) -> str:
    value = os.getenv(name, default)

    if required and (value is None or str(value).strip() == ""):
        raise RuntimeError(f"Missing required environment variable: {name}")

    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return str(value)


def get_int_env(name: str, default: int | None = None, *, required: bool = False) -> int:
    raw_default = str(default) if default is not None else None
    raw_value = get_env(name, raw_default, required=required)

    try:
        return int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid integer environment variable: {name}") from exc


def get_bool_env(name: str, default: bool = False) -> bool:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


def get_app_env() -> str:
    return get_env("APP_ENV", "development").strip().lower()


def should_enable_docs() -> bool:
    if "ENABLE_DOCS" in os.environ:
        return get_bool_env("ENABLE_DOCS")

    return get_app_env() != "production"


def get_database_url() -> str:
    return get_env("DATABASE_URL", required=True)


def get_redis_url() -> str:
    return get_env("REDIS_URL", required=True)


def validate_runtime_config() -> None:
    get_database_url()
    get_redis_url()
    get_env("SMTP_HOST", required=True)
    get_int_env("SMTP_PORT", required=True)
    get_env("SMTP_USERNAME", required=True)
    get_env("SMTP_PASSWORD", required=True)
    get_env("EMAIL_FROM", required=True)
    get_env("INTERNAL_API_KEY", required=True)
