from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, VARCHAR, REAL, TEXT
from sqlalchemy.orm import relationship

from models.base import Base


class City(Base):
    __tablename__ = 'city'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(50), nullable=False)
    lat = Column(REAL, nullable=False)
    lon = Column(REAL, nullable=False)
    url = Column(TEXT, nullable=False)

    user = relationship('User', secondary='user_city')
