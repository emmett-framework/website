FROM FROM docker.io/library/python:3.9-slim

WORKDIR /root
RUN apt-get -qq update -y && apt-get -q install -y curl gcc git
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
ENV PATH /root/.poetry/bin:$PATH
RUN poetry config virtualenvs.in-project true

RUN mkdir -p /usr/src/deps
COPY pyproject.toml /usr/src/deps
COPY poetry.lock /usr/src/deps
WORKDIR /usr/src/deps
RUN poetry install --no-dev
ENV PATH /usr/src/deps/.venv/bin:$PATH

WORKDIR /app

COPY app app
COPY build/dist/version/version.yml app/config/version.yml
COPY build/dist/docs app/docs

EXPOSE 8000

ENTRYPOINT [ "emmett" ]
CMD [ "serve", "--no-access-log", "--max-concurrency", "512" ]
