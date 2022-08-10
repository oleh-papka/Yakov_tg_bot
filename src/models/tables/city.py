from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, REAL, TEXT
from sqlalchemy.orm import relationship

from models.base import Base


class City(Base):
    __tablename__ = 'city'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=False)
    lat = Column(REAL, nullable=True)
    lon = Column(REAL, nullable=True)
    url = Column(TEXT, nullable=True)
    timezone_offset = Column(INTEGER, nullable=True)

    user = relationship('User', secondary='user_city')
