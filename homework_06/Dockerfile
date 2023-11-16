FROM python:3.9-alpine

WORKDIR /hasker

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

COPY . .

RUN pip install -r requirements.txt