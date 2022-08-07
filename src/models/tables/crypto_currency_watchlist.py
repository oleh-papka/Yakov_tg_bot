from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER

from models.base import Base


class CryptoCurrencyWatchlist(Base):
    __tablename__ = 'crypto_currency_watchlist'

    user_id = Column(INTEGER, ForeignKey('user.id'), primary_key=True)
    crypto_currency_id = Column(INTEGER, ForeignKey('crypto_currency.id'), primary_key=True)
