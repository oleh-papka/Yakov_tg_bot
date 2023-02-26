from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Currency, User


async def get_curr_by_user_id(session: AsyncSession, user_id: int) -> list | None:
    """Retrieve currency by user_id"""

    query = await select(Currency).filter(User.id == user_id, User.currency)
    result = await session.execute(query)
    rows = result.scalars().all()

    return rows


async def get_curr_by_name(session: AsyncSession, name: str) -> Currency:
    """Retrieve currency by name"""

    query = await select(Currency).where(Currency.name == name)
    result = await session.execute(query)
    row = result.scalars().first()

    return row
