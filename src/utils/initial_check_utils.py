from sqlalchemy import create_engine
from sqlalchemy.engine import Inspector
from sqlalchemy.exc import SQLAlchemyError

from config import Config


def check_db_connection() -> bool:
    engine = create_engine(Config.DB_URL)
    try:
        engine.connect()
        return True
    except SQLAlchemyError:
        return False


def check_db_tables() -> bool:
    engine = create_engine(Config.DB_URL)
    engine.connect()

    inspector = Inspector.from_engine(engine)

    if len(inspector.get_table_names()) == 9:  # with current setup there should be 9 tables
        return True
    else:
        return False
