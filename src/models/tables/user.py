from datetime import datetime

from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, BOOLEAN
from sqlalchemy.orm import relationship

from ..base import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER, primary_key=True)
    username = Column(VARCHAR(64), nullable=True)
    first_name = Column(VARCHAR(64), nullable=False)
    last_name = Column(VARCHAR(64), nullable=True)
    joined = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    language_code = Column(VARCHAR(2), nullable=False)
    timezone_offset = Column(INTEGER, nullable=True, default=10800)
    active = Column(BOOLEAN, nullable=False, default=True)

    city = relationship('City', secondary='user_city', overlaps='user')
    currency = relationship('Currency', secondary='currency_watchlist', overlaps='user')
    crypto_currency = relationship('CryptoCurrency', secondary='crypto_currency_watchlist', overlaps='user')
