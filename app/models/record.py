from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True)

    source_id = Column(Integer, ForeignKey("sources.id"))

    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    summary = Column(String)

    hash = Column(String, index=True)

    published_at = Column(DateTime)

    collected_at = Column(DateTime(timezone=True), server_default=func.now())