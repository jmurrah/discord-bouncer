FROM python:3.10-slim

WORKDIR /app
RUN pip install poetry

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

ENV TZ=America/Chicago
ENV GOOGLE_APPLICATION_CREDENTIALS=service-account-credentials.json

CMD ["poetry", "run", "bouncer"]