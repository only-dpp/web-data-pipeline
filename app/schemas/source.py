from pydantic import BaseModel


class SourceCreate(BaseModel):
    name: str
    base_url: str
    list_url: str
    list_selector: str
    title_selector: str
    link_selector: str
    summary_selector: str | None = None
    schedule_minutes: int = 60


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