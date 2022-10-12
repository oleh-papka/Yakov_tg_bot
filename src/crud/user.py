import logging

import telegram
from sqlalchemy import update
from sqlalchemy.orm import Session

import models

logger = logging.getLogger(__name__)


def get_user(db: Session, user_id: int) -> models.User:
    """Retrieve user by user_id"""
    user = db.query(
        models.User
    ).filter(
        models.User.id == user_id
    ).first()

    return user


def get_all_users(db: Session, active_flag: None | bool = None) -> list:
    """Retrieve all users from db"""
    if active_flag:
        users = db.query(
            models.User
        ).filter(
            models.User.active == True
        ).all()
    else:
        users = db.query(
            models.User
        ).all()

    return users


def create_user(db: Session, user: telegram.User) -> models.User:
    """Creates user in db"""
    user_model = models.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )

    db.add(user_model)
    db.commit()

    return user_model


def update_user(db: Session, user: telegram.User, user_data: dict) -> None:
    """Update specific parameter for user"""
    update_query = update(
        models.User
    ).where(
        models.User.id == user.id
    ).values(user_data)

    db.execute(update_query)
    db.commit()

    changes = [f"'{key}'->'{value}'" for key, value in user_data.items()]
    changes = ' '.join(changes)

    logger.debug(f'Changed: {changes} for user {user.name} (id:{user.id})')


def user_update_multiple(db: Session,
                         user: telegram.User, user_model: models.User) -> None:
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
        update_user(db, user, user_data)
    else:
        logger.debug(f'Nothing to change for user {user.name} (id:{user.id})')


def create_or_update_user(db: Session, user: telegram.User) -> models.User:
    """Create new user or update user info if needed"""
    if user_model := get_user(db, user.id):
        user_update_multiple(db, user, user_model)
    else:
        user_model = create_user(db, user)

    return user_model
