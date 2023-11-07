from datetime import time, timedelta, datetime

from sqlalchemy import select, literal, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from models.tables.repeated_action import RepeatedAction


async def get_actions(session: AsyncSession,
                      user_id: int | None = None,
                      action_id: int | None = None,
                      execution_time: time | None = None,
                      action: str | None = None) -> [RepeatedAction]:
    """Retrieve repeated_actions by user_id"""

    if action_id:
        query = select(RepeatedAction).where(RepeatedAction.id == literal(action_id))
    elif user_id:
        if execution_time and action:
            today = datetime.now().date()
            execution_datetime = datetime.combine(today, execution_time)

            time_30_minutes_ago = execution_datetime - timedelta(minutes=30)
            time_30_minutes_later = execution_datetime + timedelta(minutes=30)

            query = (
                select(RepeatedAction)
                .where(
                    and_(
                        RepeatedAction.user_id == literal(user_id),
                        RepeatedAction.action == literal(action),
                        RepeatedAction.execution_time >= time_30_minutes_ago.time(),
                        RepeatedAction.execution_time <= time_30_minutes_later.time()
                    )
                )
                .order_by(RepeatedAction.execution_time, RepeatedAction.action)
            )
        else:
            query = (
                select(RepeatedAction)
                .where(RepeatedAction.user_id == literal(user_id))
            )
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


async def delete_action(session: AsyncSession,
                        action_id: int) -> None:
    """Deletes repeated_action"""

    delete_query = (
        delete(RepeatedAction)
        .where(RepeatedAction.id == literal(action_id))
    )

    await session.execute(delete_query)
    await session.commit()
