from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR
from sqlalchemy.orm import relationship

from ..base import Base


class CryptoCurrency(Base):
    __tablename__ = 'crypto_currency'

    id = Column(INTEGER, primary_key=True)
    name = Column(VARCHAR(20), nullable=False)
    abbr = Column(VARCHAR(10), nullable=False)

    user = relationship('User', secondary='crypto_currency_watchlist')
