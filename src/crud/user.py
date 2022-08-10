import telegram
from sqlalchemy import update

import models
from config import Config


def get_user(db, user_id: int) -> models.User:
    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    return user


def create_user(db, user: telegram.User) -> models.User:
    user_model = models.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )

    db.add(user_model)
    db.commit()

    Config.LOGGER.info(f'Added new user {user.name} (id:{user.id})')
    return user_model


def update_user(db, user: telegram.User, user_data: dict) -> None:
    update_query = update(
        models.User
    ).where(
        models.User.id == user.id
    ).values(user_data)

    db.execute(update_query)
    db.commit()

    changes = [f"'{key}'->'{value}'" for key, value in user_data.items()]
    changes = ' '.join(changes)

    Config.LOGGER.debug(f'Changed: {changes} for user {user.name} (id:{user.id})')


def auto_update_user(db, user: telegram.User, user_model: models.User) -> None:
    """Update user if needed"""
    user_data = {}

    if user_model.username != user.username:
        user_data['username'] = user.username
    if user_model.first_name != user.first_name:
        user_data['first_name'] = user.first_name
    if user_model.last_name != user.last_name:
        user_data['last_name'] = user.last_name
    if user_model.language_code != user.language_code:
        user_data['language_code'] = user.language_code

    if user_data:
        update_user(db, user, user_data)
    else:
        Config.LOGGER.debug(f'Nothing to change for user {user.name} (id:{user.id})')


def auto_create_user(db, user: telegram.User) -> models.User:
    """Create new user or update its data if needed"""
    if user_model := get_user(db, user.id):
        auto_update_user(db, user, user_model)
    else:
        user_model = create_user(db, user)
    return user_model
