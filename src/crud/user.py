import telegram
from loguru import logger
from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from src import models


async def get_user(session: AsyncSession, user_id: int) -> models.User:
    """Retrieve user by user_id"""

    result = await session.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalars().first()

    return user


async def get_all_users(session: AsyncSession, active_flag: None | bool = None):
    """Retrieve all users from session"""

    if active_flag:
        users = await session.execute(select(models.User).where(models.User.active == True))
    else:
        users = await session.execute(select(models.User))

    return users.scalars().all()


async def create_user(session: AsyncSession, user: telegram.User) -> models.User:
    """Creates user in session"""

    user_model = models.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )

    session.add(user_model)
    await session.commit()

    return user_model


async def update_user(session: AsyncSession, user: telegram.User, user_data: dict) -> None:
    """Update specific parameter for user"""

    update_query = update(models.User).where(models.User.id == user.id).values(user_data)

    await session.execute(update_query)
    await session.commit()

    changes = [f"'{key}'->'{value}'" for key, value in user_data.items()]
    changes = ' '.join(changes)

    logger.info(f'Changed: {changes} for user {user.name} (id:{user.id})')


async def user_update_multiple(session: AsyncSession,
                               user: telegram.User,
                               user_model: models.User) -> None:
    """Update user if needed according to telegram.User object"""

    user_data = {}

    if user_model.username != user.username:
        user_data['username'] = user.username
    if user_model.first_name != user.first_name:
        user_data['first_name'] = user.first_name
    if user_model.last_name != user.last_name:
        user_data['last_name'] = user.last_name
    if user_model.language_code != user.language_code:
        user_data['language_code'] = user.language_code
    if not user_model.active:
        user_data['active'] = True

    if user_data:
        await update_user(session, user, user_data)
    else:
        logger.info(f'Nothing to change for user {user.name} (id:{user.id})')


async def create_or_update_user(session: AsyncSession, user: telegram.User) -> models.User:
    """Create new user or update user info if needed"""

    if user_model := await get_user(session, user.id):
        await user_update_multiple(session, user, user_model)
    else:
        user_model = await create_user(session, user)

    return user_model
