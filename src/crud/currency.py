from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession

from models import Currency, User


async def get_curr_by_user_id(session: AsyncSession, user_id: int):
    """Retrieve currency by user_id"""

    query = select(Currency).filter(User.id == literal(user_id), User.currency)
    result = await session.execute(query)
    rows = result.scalars().all()

    return rows


async def get_curr_by_name(session: AsyncSession, name: str) -> Currency:
    """Retrieve currency by name"""

    query = select(Currency).where(Currency.name == literal(name))
    result = await session.execute(query)
    row = result.scalars().first()

    return row
