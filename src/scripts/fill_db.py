from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from config import Config


def create_all_coins():
    engine = create_engine(Config.DB_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    crypto_models = [
        models.CryptoCurrency(id=1, name='Bitcoin', abbr='BTC'),
        models.CryptoCurrency(id=1027, name='Ethereum', abbr='ETH'),
        models.CryptoCurrency(id=1839, name='BNB', abbr='BNB'),
        models.CryptoCurrency(id=5426, name='Solana', abbr='SOL'),
        models.CryptoCurrency(id=52, name='XRP', abbr='XRP'),
        models.CryptoCurrency(id=74, name='Dogecoin', abbr='DOGE')
    ]

    with session as db:
        for crypto_model in crypto_models:
            db.add(crypto_model)

        db.commit()
