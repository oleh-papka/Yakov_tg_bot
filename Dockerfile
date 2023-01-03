FROM python:3.11-alpine

COPY requirements.txt .env ./

RUN pip install -r requirements.txt

WORKDIR /bot

COPY src /bot/src
COPY alembic /bot/alembic
COPY alembic.ini /bot/

CMD export $(xargs < /.env) && python3 src/main.py