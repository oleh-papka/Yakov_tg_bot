from sqlalchemy.orm import Session

from models import Currency, User


def get_curr_by_user_id(db: Session, user_id: int) -> list | None:
    rows = db.query(
        Currency
    ).filter(
        User.id == user_id,
        User.currency
    ).all()

    return rows


def get_curr_by_name(db: Session, name: str) -> Currency:
    row = db.query(
        Currency
    ).filter(
        Currency.name == name
    ).first()

    return row
