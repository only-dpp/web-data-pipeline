from sqlalchemy.orm import Session

from app.models.record import Record


def list_records(db: Session, source_id: int | None = None) -> list[Record]:
    query = db.query(Record)

    if source_id is not None:
        query = query.filter(Record.source_id == source_id)

    return query.order_by(Record.id.desc()).all()