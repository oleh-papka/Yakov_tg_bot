FROM python:3.11-alpine

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY src /bot/src
COPY alembic /bot/alembic
COPY alembic.ini /bot/

CMD ["python", "src/main.py"]