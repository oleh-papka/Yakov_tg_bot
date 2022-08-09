from datetime import datetime

from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR
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
    timezone = Column(VARCHAR(30), nullable=True, default='Europe/Kiev')

    city = relationship('City', secondary='user_city', overlaps='user')
    currency = relationship('Currency', secondary='currency_watchlist', overlaps='user')
