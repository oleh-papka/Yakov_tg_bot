from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER

from models.base import Base


class CurrencyWatchlist(Base):
    __tablename__ = 'currency_watchlist'

    user_id = Column(INTEGER, ForeignKey('user.id'), primary_key=True)
    currency_id = Column(INTEGER, ForeignKey('currency.id'), primary_key=True)
