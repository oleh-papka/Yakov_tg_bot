from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, FLOAT

from models.base import Base


class Account(Base):
    __tablename__ = 'account'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, ForeignKey('user.id'), nullable=False)
    currency_id = Column(INTEGER, ForeignKey('currency.id'), nullable=True)
    crypto_currency_id = Column(INTEGER, ForeignKey('crypto_currency.id'), nullable=True)
    type = Column(VARCHAR(50), nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    balance = Column(FLOAT, nullable=False)
