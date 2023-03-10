from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CryptoCurrency, User


async def get_crypto_by_user_id(session: AsyncSession, user_id: int):
    """Retrieve cryptocurrency by user_id"""

    query = select(CryptoCurrency).filter(User.id == user_id, User.crypto_currency)
    result = await session.execute(query)
    rows = result.scalars().all()

    return rows


async def get_crypto_by_abbr(session: AsyncSession, abbr: str) -> CryptoCurrency:
    """Retrieve cryptocurrency by abbr"""

    query = select(CryptoCurrency).where(CryptoCurrency.abbr == abbr)
    result = await session.execute(query)
    row = result.scalars().first()

    return row
