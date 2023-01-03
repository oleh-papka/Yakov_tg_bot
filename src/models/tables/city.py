from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, REAL, TEXT
from sqlalchemy.orm import relationship

from models.base import Base


class City(Base):
    __tablename__ = 'city'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    owm_id = Column(INTEGER, nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    local_name = Column(VARCHAR(50), nullable=True)
    lat = Column(REAL, nullable=True)
    lon = Column(REAL, nullable=True)
    sinoptik_url = Column(TEXT, nullable=True)
    timezone_offset = Column(INTEGER, nullable=True)

    user = relationship('User', secondary='user_city')
