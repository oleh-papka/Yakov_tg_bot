from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, REAL, TEXT
from sqlalchemy.orm import relationship

from ..base import Base


class City(Base):
    __tablename__ = 'city'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, ForeignKey('user.id'), nullable=False)
    owm_id = Column(INTEGER, nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    local_name = Column(VARCHAR(50), nullable=True)
    lat = Column(REAL, nullable=True)
    lon = Column(REAL, nullable=True)
    sinoptik_url = Column(TEXT, nullable=True)
    timezone_offset = Column(INTEGER, nullable=True)

    user = relationship('User')
