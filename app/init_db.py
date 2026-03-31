from sqlalchemy import text

from app.database import Base, engine
from app.models.article import Article
from app.models.digest_dispatch import DigestDispatch
from app.models.email_delivery import EmailDelivery
from app.models.record import Record
from app.models.run import Run
from app.models.source import Source
from app.models.subscriber import Subscriber


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                ALTER TABLE subscribers
                ADD COLUMN IF NOT EXISTS welcome_sent_at TIMESTAMPTZ
                """
            )
        )
        connection.execute(
            text(
                """
                ALTER TABLE subscribers
                ADD COLUMN IF NOT EXISTS last_digest_sent_at TIMESTAMPTZ
                """
            )
        )


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
