from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Feedback


async def get_feedback_by_msg_id(session: AsyncSession, msg_id: int) -> Feedback:
    """Retrieve feedback from msg_id"""

    query = await select(Feedback).where(Feedback.msg_id == msg_id)
    result = await session.execute(query)
    feedback = result.scalars().first()

    return feedback


async def get_feedback_by_user_id(session: AsyncSession, user_id: int) -> list:
    """Retrieve feedbacks from user_id"""

    query = await select(Feedback).where(Feedback.user_id == user_id)
    result = await session.execute(query)
    feedbacks = result.scalars().all()

    return feedbacks


async def mark_feedback_read(session: AsyncSession, msg_id: int) -> None:
    """Update read_flag for feedback by message_id"""

    query = await select(Feedback).where(Feedback.msg_id == msg_id)
    result = await session.execute(query)
    feedback = result.scalars().first()

    feedback.read_flag = True
    await session.commit()
