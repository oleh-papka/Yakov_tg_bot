from datetime import datetime

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import INTEGER, TEXT, TIMESTAMP
from sqlalchemy.orm import relationship

from ..base import Base


class FeedbackReply(Base):
    __tablename__ = 'feedback_reply'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    feedback_id = Column(INTEGER, ForeignKey('feedback.id'), nullable=False)
    msg_id = Column(INTEGER, nullable=False)
    msg_text = Column(TEXT, nullable=False)
    timestamp = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    feedback = relationship('Feedback', lazy='immediate')
