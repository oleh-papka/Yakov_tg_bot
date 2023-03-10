import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models

os.system("alembic upgrade head")

crypto_models = [
    models.CryptoCurrency(id=1, name='Bitcoin', abbr='BTC'),
    models.CryptoCurrency(id=1027, name='Ethereum', abbr='ETH'),
    models.CryptoCurrency(id=1839, name='BNB', abbr='BNB'),
    models.CryptoCurrency(id=5426, name='Solana', abbr='SOL'),
    models.CryptoCurrency(id=52, name='XRP', abbr='XRP'),
    models.CryptoCurrency(id=74, name='Dogecoin', abbr='DOGE')
]

curr_models = [
    models.Currency(name='usd', symbol='🇺🇸'),
    models.Currency(name='eur', symbol='🇪🇺'),
    models.Currency(name='pln', symbol='🇵🇱'),
    models.Currency(name='gbp', symbol='🇬🇧')
]

if __name__ == '__main__':
    engine = create_engine(
        os.getenv('DB_URL').replace('+asyncpg', ''))  # Mind that synchronous URL should be used, but I got you
    Session = sessionmaker(bind=engine)

    with Session() as db:
        print('==> Populating crypto_currency table...')
        for crypto_model in crypto_models:
            db.add(crypto_model)

        db.commit()
        print('==> Table crypto_currency populated successfully!')

        print('==> Populating currency table...')
        for curr_model in curr_models:
            db.add(curr_model)

        db.commit()
        print('==> Table currency populated successfully!')
