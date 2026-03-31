from pydantic import BaseModel, Field, field_validator

from app.core.url_security import validate_source_url


class SourceCreate(BaseModel):
    name: str
    base_url: str
    list_url: str
    list_selector: str
    title_selector: str
    link_selector: str
    summary_selector: str | None = None
    schedule_minutes: int = Field(default=60, ge=1)

    @field_validator("base_url", "list_url")
    @classmethod
    def validate_urls(cls, value: str) -> str:
        return validate_source_url(value)


class SourceResponse(BaseModel):
    id: int
    name: str
    base_url: str
    list_url: str
    list_selector: str
    title_selector: str
    link_selector: str
    summary_selector: str | None = None
    schedule_minutes: int

    model_config = {"from_attributes": True}
