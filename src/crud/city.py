from sqlalchemy.orm import Session

from models import City, User


# TODO: add to db column local_name,
#  change url to sinoptik_url
def get_city_by_name(db: Session, city_name: str) -> City | None:
    city_model = db.query(
        City
    ).filter(
        City.name == city_name
    ).first()

    return city_model


def get_city_by_user(db: Session, user_id: int) -> tuple | None:
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
                lat: float,
                lon: float,
                url: str = None,
                timezone_offset: int = None) -> City:
    city_model = City(
        owm_id=owm_id,
        name=name,
        lat=lat,
        lon=lon,
        url=url,
        timezone_offset=timezone_offset
    )

    db.add(city_model)
    db.commit()

    return city_model
