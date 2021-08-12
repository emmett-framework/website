FROM docker.io/library/python:3.9-slim as builder

RUN apt-get -qq update -y && apt-get -q install -y curl gcc git
RUN curl https://raw.githubusercontent.com/gi0baro/poetry-bin/master/install.sh | sh
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml .
COPY poetry.lock .
RUN poetry install --no-dev

FROM docker.io/library/python:3.9-slim

COPY --from=builder /.venv /.venv
ENV PATH /.venv/bin:$PATH

WORKDIR /app
COPY app app
COPY build/dist/version/version.yml app/config/version.yml
COPY build/dist/docs app/docs

EXPOSE 8000

ENTRYPOINT [ "emmett" ]
CMD [ "serve", "--no-access-log", "--max-concurrency", "512" ]
