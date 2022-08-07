from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER

from models.base import Base


class UserCity(Base):
    __tablename__ = 'user_city'

    city_id = Column(INTEGER, ForeignKey('city.id'), primary_key=True)
    user_id = Column(INTEGER, ForeignKey('user.id'), primary_key=True)
