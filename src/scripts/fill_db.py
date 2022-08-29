from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from config import Config


def _create_session():
    engine = create_engine(Config.DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def populate_crypto_currency():
    crypto_models = [
        models.CryptoCurrency(id=1, name='Bitcoin', abbr='BTC'),
        models.CryptoCurrency(id=1027, name='Ethereum', abbr='ETH'),
        models.CryptoCurrency(id=1839, name='BNB', abbr='BNB'),
        models.CryptoCurrency(id=5426, name='Solana', abbr='SOL'),
        models.CryptoCurrency(id=52, name='XRP', abbr='XRP'),
        models.CryptoCurrency(id=74, name='Dogecoin', abbr='DOGE')
    ]

    with _create_session() as db:
        for crypto_model in crypto_models:
            db.add(crypto_model)

        db.commit()


def populate_currency():
    curr_models = [
        models.Currency(name='usd', symbol='🇺🇸'),
        models.Currency(name='eur', symbol='🇪🇺'),
        models.Currency(name='pln', symbol='🇵🇱'),
        models.Currency(name='gbp', symbol='🇬🇧')
    ]

    with _create_session() as db:
        for curr_model in curr_models:
            db.add(curr_model)

        db.commit()
