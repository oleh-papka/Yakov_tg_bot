import models


def get_crypto_by_user(db, user_id: int) -> tuple | None:
    rows = db.query(
        models.CryptoCurrency
    ).filter(
        models.User.id == user_id,
        models.User.crypto_currency
    ).all()

    return rows


def get_crypto_by_abbr(db, abbr):
    row = db.query(
        models.CryptoCurrency
    ).filter(
        models.CryptoCurrency.abbr == abbr
    ).first()

    return row
