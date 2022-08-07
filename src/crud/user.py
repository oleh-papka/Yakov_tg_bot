import telegram
from sqlalchemy import select, update
from telegram import Update
from telegram.ext import CallbackContext

import models
from config import Config
from utils.db_utils import session


def user_exists(user_id: int) -> models.User:
    with session as db:
        user = db.execute(
            select(
                models.User
            ).where(
                models.User.id == user_id
            )
        ).first()

    if user:
        user = user[0]

    return user


def create_user(user: telegram.User):
    user_model = models.User(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )

    with session as db:
        db.add(user_model)
        db.commit()

    Config.LOGGER.info(f'Added new user {user.name} (id:{user.id})')


def update_user(user: telegram.User, user_model: models.User):
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
        update_query = update(
            models.User
        ).where(
            models.User.id == user.id
        ).values(user_data)

        with session as db:
            db.execute(update_query)
            db.commit()

        changes = [f'{key} -> {value}' for key, value in user_data.items()]

        Config.LOGGER.info(f'Changed {changes} for user {user.name} (id:{user.id})')
    else:
        Config.LOGGER.debug(f'Nothing to change for user {user.name} (id:{user.id})')


def add_user_to_db(func):
    def inner_function(update: Update, context: CallbackContext):
        message = update.message
        user = message.from_user

        if user_model := user_exists(user.id):
            update_user(user, user_model)
        else:
            create_user(user)

        return func(update, context)

    return inner_function
