from sqlalchemy import select
from sqlalchemy.engine import Row
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from src.models import City, User


async def get_city(session: AsyncSession, city_name: str) -> City | None:
    """Retrieve city by city_name"""

    query = select(City).where(City.name == city_name)
    result = await session.execute(query)
    city = result.scalars().first()

    return city


async def get_user_city(session: AsyncSession, user_id: int) -> Row[City, User] | None:
    """Retrieve city by user_id"""

    query = select(City, User).filter(User.id == user_id, User.city)
    result = await session.execute(query)
    row = result.scalars().first()

    return row


def create_city(session: AsyncSession,
                owm_id: int,
                name: str,
                local_name: str,
                lat: float,
                lon: float,
                sinoptik_url: str = None,
                timezone_offset: int = None) -> City:
    """Create city"""

    city_model = City(
        owm_id=owm_id,
        name=name,
        local_name=local_name,
        lat=lat,
        lon=lon,
        sinoptik_url=sinoptik_url,
        timezone_offset=timezone_offset
    )

    session.add(city_model)
    await session.commit()

    return city_model
