from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config


def create_session(func):
    def wrapper(*args, **kwargs):
        engine = create_engine(Config.DB_URL)
        session = sessionmaker(bind=engine)

        with session() as db:
            res = func(*args, **kwargs, db=db)

        return res

    return wrapper
