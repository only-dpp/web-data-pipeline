from sqlalchemy.orm import Session

from app.models.run import Run


def list_runs(db: Session) -> list[Run]:
    return db.query(Run).order_by(Run.id.desc()).all()