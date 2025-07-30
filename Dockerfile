FROM python:3.13 AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

FROM node:16 AS css

COPY front wrk/front
COPY app/templates wrk/app/templates
WORKDIR /wrk/front

ENV NODE_ENV=production

RUN npm ci --also=dev && npx tailwindcss -i src/tailwind.css -c tailwind.config.js -o dist/main.css --minify

FROM python:3.13-slim AS docs

RUN apt-get update -y && apt-get install -y git

COPY build wrk/build
WORKDIR /wrk/build

RUN pip install pyyaml
RUN python docs.py

FROM python:3.13-slim

COPY --from=builder /.venv /.venv
ENV PATH=/.venv/bin:$PATH

WORKDIR /app
COPY app app
COPY --from=css /wrk/front/dist/main.css app/static/bundled/main.css
COPY --from=docs /wrk/build/dist/version/version.yml app/config/version.yml
COPY --from=docs /wrk/build/dist/docs app/docs

EXPOSE 8000

ENTRYPOINT [ "emmett" ]
CMD [ "serve", "--host", "0.0.0.0" ]
