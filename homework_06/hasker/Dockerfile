FROM python:3.10.9

WORKDIR /hasker

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

COPY . .

RUN pip install -r requirements.txt
