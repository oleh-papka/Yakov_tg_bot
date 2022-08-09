import telegram

import models
from config import Config


def get_city_by_name(db, city_name: str) -> models.City:
    city = db.query(
        models.City
    ).filter(
        models.City.name == city_name
    ).first()

    return city


def get_city_by_user(db, user_id: int) -> models.City:
    city = db.query(
        models.City
    ).join(
        models.City.user
    ).filter(
        models.User.id == user_id
    ).first()

    return city


def create_city(db, user: telegram.User, name: str, lat: float, lon: float, url: str) -> None:
    city_model = models.City(
        name=name,
        lat=lat,
        lon=lon,
        url=url
    )

    db.add(city_model)
    user_model = db.query(models.User).filter(models.User.id == user.id).first()
    user_model.city.append(city_model)
    db.commit()

    Config.LOGGER.debug(f'Added new city {name} for user {user.name} (id:{user.id})')
