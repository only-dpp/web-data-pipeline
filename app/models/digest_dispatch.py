from sqlalchemy import Column, Date, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database import Base


class DigestDispatch(Base):
    __tablename__ = "digest_dispatches"

    id = Column(Integer, primary_key=True, index=True)
    digest_date = Column(Date, unique=True, index=True, nullable=False)
    status = Column(String, nullable=False, default="running")
    hours = Column(Integer, nullable=False, default=24)
    limit = Column(Integer, nullable=False, default=10)
    subscribers_targeted = Column(Integer, nullable=False, default=0)
    subscribers_sent = Column(Integer, nullable=False, default=0)
    subscribers_failed = Column(Integer, nullable=False, default=0)
    error_message = Column(String)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    finished_at = Column(DateTime(timezone=True))
