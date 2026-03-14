from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True)

    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)

    title = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    summary = Column(String)

    hash = Column(String, unique=True, index=True, nullable=False)

    published_at = Column(DateTime)
    collected_at = Column(DateTime(timezone=True), server_default=func.now())