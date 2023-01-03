from sqlalchemy.orm import Session

from models import CryptoCurrency, User


def get_crypto_by_user_id(db: Session,
                          user_id: int) -> list[CryptoCurrency] | None:
    rows = db.query(
        CryptoCurrency
    ).filter(
        User.id == user_id,
        User.crypto_currency
    ).all()

    return rows


def get_crypto_by_abbr(db: Session, abbr: str) -> CryptoCurrency:
    row = db.query(
        CryptoCurrency
    ).filter(
        CryptoCurrency.abbr == abbr
    ).first()

    return row
