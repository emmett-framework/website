FROM python:3.8-alpine

RUN apk add --no-cache libstdc++

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app
RUN apk add --no-cache --virtual build-deps \
    g++ musl-dev make git libffi-dev libuv-dev openssl-dev && \
    pip install -r /usr/src/app/requirements.txt && \
    apk del build-deps

WORKDIR /app

COPY app app
COPY build/dist/version/version.yml app/config/version.yml
COPY build/dist/docs app/docs

EXPOSE 8000

ENTRYPOINT [ "emmett" ]
CMD [ "serve", "--no-access-log", "--max-queue", "512" ]
