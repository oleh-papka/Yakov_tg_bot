import models


def get_curr_by_user(db, user_id: int) -> tuple | None:
    rows = db.query(
        models.Currency
    ).filter(
        models.User.id == user_id,
        models.User.currency
    ).all()

    return rows


def get_curr_by_name(db, name):
    row = db.query(
        models.Currency
    ).filter(
        models.Currency.name == name
    ).first()

    return row
