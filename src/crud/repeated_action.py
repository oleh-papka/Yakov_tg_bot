from datetime import time

from sqlalchemy import select, literal
from sqlalchemy.ext.asyncio import AsyncSession

from models.tables.repeated_action import RepeatedAction


async def get_actions(session: AsyncSession, user_id: int | None = None) -> [RepeatedAction]:
    """Retrieve repeated_actions by user_id"""

    if user_id:
        query = select(RepeatedAction).where(RepeatedAction.user_id == literal(user_id))
    else:
        query = select(RepeatedAction)

    result = await session.execute(query)
    repeated_actions = result.scalars().all()

    return repeated_actions


async def create_action(session: AsyncSession,
                        user_id: int,
                        action: str,
                        execution_time: time) -> None:
    """Adds repeated_action"""

    repeated_action_model = RepeatedAction(user_id=user_id,
                                           action=action,
                                           execution_time=execution_time)
    session.add(repeated_action_model)
    await session.commit()
