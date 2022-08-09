from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import Config


def create_session(func):
    def wrapper(*args, **kwargs):
        engine = create_engine(Config.DB_URL)
        Session = sessionmaker(bind=engine)
        session = Session()

        with session as db:
            res = func(*args, **kwargs, db=session)

        return res

    return wrapper
