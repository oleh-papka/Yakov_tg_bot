from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, TIMESTAMP, BOOLEAN
from sqlalchemy.orm import relationship

from ..base import Base


class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    user_id = Column(INTEGER, ForeignKey('user.id'), nullable=False)
    msg_id = Column(INTEGER, nullable=False)
    msg_text = Column(TEXT, nullable=False)
    read_flag = Column(BOOLEAN, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    user = relationship('User', lazy="immediate")
