from loguru import logger

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, ContextTypes

from src.models import User
from src.utils import escape_md2_no_links
from src.utils.db_utils import get_session


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.success("Start command")
    user = update.effective_user

    # Create a new user instance and add it to the database
    async with get_session() as session:
        user_model = User(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            language_code=user.language_code
        )
        session.add(user_model)
        await session.commit()

    logger.success(f"Added new user: {user.name}")

    msg = (f"Привіт {user.first_name}, я Yakov і створений тому, що моєму [розробнику]"
           "(tg://user?id={Config.CREATOR_ID}) було нудно.\nЯ постійно отримую апдейти "
           "та нові функції, залишайся зі мною, розробнику приємно, а тобі цікаві фішки 🙃\n\n"
           "Підказка - /help\n\nP.S. Підтримати ЗСУ можна [тут]"
           "(https://savelife.in.ua/donate/#payOnce), Слава Україні!")

    await update.message.reply_text(escape_md2_no_links(msg),
                                    parse_mode=ParseMode.MARKDOWN_V2,
                                    disable_web_page_preview=True)


start_command_handler = CommandHandler('start', start)
