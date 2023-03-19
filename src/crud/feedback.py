from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Feedback


async def get_feedback_by_msg_id(session: AsyncSession, msg_id: int) -> Feedback:
    """Retrieve feedback from msg_id"""

    query = select(Feedback).where(Feedback.msg_id == msg_id)
    result = await session.execute(query)
    feedback = result.scalars().first()

    return feedback


async def get_feedback_by_user_id(session: AsyncSession, user_id: int):
    """Retrieve feedbacks from user_id"""

    query = select(Feedback).where(Feedback.user_id == user_id)
    result = await session.execute(query)
    feedbacks = result.scalars().all()

    return feedbacks


async def mark_feedback_read(session: AsyncSession, msg_id: int) -> None:
    """Update read_flag for feedback by message_id"""

    query = select(Feedback).where(Feedback.msg_id == msg_id)
    result = await session.execute(query)
    feedback = result.scalars().first()

    feedback.read_flag = True
    await session.commit()


async def create_feedback(session: AsyncSession,
                          feedback_type: str,
                          user_id: int,
                          msg_id: int,
                          msg_text: str,
                          read_flag: None | bool = None) -> None:
    """Adds feedback"""

    if read_flag is None:
        read_flag = False

    feedback_model = Feedback(user_id=user_id,
                              feedback_type=feedback_type,
                              msg_id=msg_id,
                              msg_text=msg_text,
                              read_flag=read_flag)
    session.add(feedback_model)
    await session.commit()


async def get_unread_feedbacks(session: AsyncSession):
    """Retrieve feedbacks from user_id"""

    query = select(Feedback).where(Feedback.read_flag == False)
    result = await session.execute(query)
    feedbacks = result.scalars().all()

    return feedbacks
