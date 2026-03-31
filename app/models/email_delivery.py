from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.sql import func

from app.database import Base


class EmailDelivery(Base):
    __tablename__ = "email_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "dispatch_id",
            "subscriber_id",
            "email_type",
            name="uq_email_deliveries_dispatch_subscriber_type",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    subscriber_id = Column(Integer, ForeignKey("subscribers.id"), nullable=False)
    dispatch_id = Column(Integer, ForeignKey("digest_dispatches.id"))
    email = Column(String, nullable=False)
    email_type = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    status = Column(String, nullable=False)
    error_message = Column(String)
    sent_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
