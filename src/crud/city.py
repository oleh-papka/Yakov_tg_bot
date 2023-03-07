from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.user import get_user_by_id
from src.models import City


async def get_city_by_name(session: AsyncSession, city_name: str) -> City | None:
    """Retrieve city by city_name"""

    query = select(City).where(City.name == city_name)
    result = await session.execute(query)
    city = result.scalars().first()

    return city


async def create_city(session: AsyncSession,
                      owm_id: int,
                      name: str,
                      local_name: str,
                      lat: float,
                      lon: float,
                      sinoptik_url: str = None,
                      timezone_offset: int = None) -> None:
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
