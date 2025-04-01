FROM python:3.12.8-alpine3.21
LABEL maintainer="koliesnichenko2018@ukr.net"

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    python3-dev \
    build-base \
    jpeg-dev \
    zlib-dev \
    make

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN mkdir -p /app/media && chmod -R 755 /app/media


RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .