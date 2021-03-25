FROM python:3.8.5-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

EXPOSE 8000

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY poetry.lock pyproject.toml ./backend/

WORKDIR /backend

RUN pip install poetry==1.1.* && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

COPY . /backend