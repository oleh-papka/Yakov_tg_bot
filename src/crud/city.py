from sqlalchemy.engine import Row
from sqlalchemy.orm import Session

from models import City, User


def get_city(db: Session, city_name: str) -> City | None:
    city_model = db.query(
        City
    ).filter(
        City.name == city_name
    ).first()

    return city_model


def get_user_city(db: Session, user_id: int) -> Row[City, User] | None:
    row = db.query(
        City,
        User
    ).filter(
        User.id == user_id,
        User.city
    ).first()

    return row


def create_city(db: Session,
                owm_id: int,
                name: str,
                local_name: str,
                lat: float,
                lon: float,
                sinoptik_url: str = None,
                timezone_offset: int = None) -> City:
    city_model = City(
        owm_id=owm_id,
        name=name,
        local_name=local_name,
        lat=lat,
        lon=lon,
        sinoptik_url=sinoptik_url,
        timezone_offset=timezone_offset
    )

    db.add(city_model)
    db.commit()

    return city_model
