import models


def get_feedback_by_msg_id(db, msg_id: int) -> models.Feedback:
    feedback = db.query(
        models.Feedback
    ).filter(
        models.Feedback.msg_id == msg_id
    ).first()

    return feedback


def get_feedback_by_user(db, user_id: int) -> models.Feedback:
    feedbacks = db.query(
        models.Feedback
    ).filter(
        models.Feedback.user_id == user_id
    ).all()

    return feedbacks


def mark_read(db, msg_id: int) -> None:
    feedback = db.query(
        models.Feedback
    ).filter(
        models.Feedback.msg_id == msg_id
    ).first()

    feedback.read_flag = True
    db.commit()
