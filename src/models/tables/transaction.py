from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, FLOAT, VARCHAR, TIMESTAMP

from models.base import Base


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    account_id = Column(INTEGER, ForeignKey('account.id'), nullable=False)
    amount = Column(FLOAT, nullable=False)
    type = Column(VARCHAR(50), nullable=False)
    description = Column(VARCHAR(50), nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
