from sqlalchemy import Column, Integer, DateTime, ForeignKey, String
from sqlalchemy.sql import func

from app.database import Base


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)

    source_id = Column(Integer, ForeignKey("sources.id"))

    status = Column(String, default="running")

    items_found = Column(Integer, default=0)
    items_new = Column(Integer, default=0)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))