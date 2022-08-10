import telegram

import models


def get_city_by_name(db, city_name: str) -> models.City | None:
    city_model = db.query(
        models.City
    ).filter(
        models.City.name == city_name
    ).first()

    return city_model


def get_city_by_user(db, user_id: int) -> tuple | None:
    row = db.query(
        models.City,
        models.User
    ).filter(
        models.User.id == user_id,
        models.User.city
    ).first()

    return row


def create_city(db, name: str, lat: float, lon: float, url: str = None, timezone_offset: int = None) -> models.City:
    city_model = models.City(
        name=name,
        lat=lat,
        lon=lon,
        url=url,
        timezone_offset=timezone_offset
    )

    db.add(city_model)
    db.commit()

    return city_model
