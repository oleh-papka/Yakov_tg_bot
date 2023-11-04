from sqlalchemy import Column, ForeignKey, VARCHAR, TIME
from sqlalchemy.dialects.postgresql import INTEGER
from sqlalchemy.orm import relationship

from ..base import Base


class RepeatedAction(Base):
    __tablename__ = 'repeated_action'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, ForeignKey('user.id'), nullable=False)
    action = Column(VARCHAR(30), nullable=False)
    execution_time = Column(TIME, nullable=False)

    user = relationship('User', lazy="immediate")
