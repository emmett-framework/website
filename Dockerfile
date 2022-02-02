FROM ghcr.io/gi0baro/poetry-bin:3.9 as builder

COPY pyproject.toml .
COPY poetry.lock .

RUN poetry install --no-dev
RUN poetry run pip install gunicorn

FROM python:3.9-slim

COPY --from=builder /.venv /.venv
ENV PATH /.venv/bin:$PATH

WORKDIR /app
COPY app app
COPY build/dist/version/version.yml app/config/version.yml
COPY build/dist/docs app/docs

EXPOSE 8000

ENTRYPOINT [ "gunicorn" ]
CMD [ "app:app", "-b", "0.0.0.0:8000", "-w", "1", "-k", "emmett.asgi.workers.EmmettWorker" ]
