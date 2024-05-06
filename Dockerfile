FROM python:3.12-slim

WORKDIR /app
RUN pip install poetry
COPY pyproject.toml poetry.lock ./

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

EXPOSE 5000

ENV FLASK_APP=./discord_bouncer/app.py
ENV FLASK_ENV=development
ENV TZ=America/Chicago

CMD [ "poetry", "run", "bouncer" ]