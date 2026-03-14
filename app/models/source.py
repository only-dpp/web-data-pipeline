from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    list_url = Column(String, nullable=False)

    list_selector = Column(String, nullable=False)
    title_selector = Column(String, nullable=False)
    link_selector = Column(String, nullable=False)
    summary_selector = Column(String)

    schedule_minutes = Column(Integer, default=60)

    created_at = Column(DateTime(timezone=True), server_default=func.now())