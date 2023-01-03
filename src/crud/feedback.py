from sqlalchemy.orm import Session

import models
from models import Feedback


def get_feedback_by_msg_id(db: Session, msg_id: int) -> Feedback:
    feedback = db.query(
        Feedback
    ).filter(
        Feedback.msg_id == msg_id
    ).first()

    return feedback


def get_feedback_by_user_id(db: Session, user_id: int) -> list:
    feedbacks = db.query(
        Feedback
    ).filter(
        Feedback.user_id == user_id
    ).all()

    return feedbacks


def mark_feedback_read(db: Session, msg_id: int) -> None:
    feedback = db.query(
        Feedback
    ).filter(
        Feedback.msg_id == msg_id
    ).first()

    feedback.read_flag = True
    db.commit()
