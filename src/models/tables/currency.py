from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR
from sqlalchemy.orm import relationship

from models.base import Base


class Currency(Base):
    __tablename__ = 'currency'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(5), nullable=False)
    symbol = Column(VARCHAR(5), nullable=False)

    user = relationship('User', secondary='currency_watchlist')
