FROM python:3.10.9

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1

EXPOSE 8000

RUN pip install --upgrade pip

RUN useradd -rms /bin/bash hasker_ad && chmod 777 /opt /run

WORKDIR /hasker

COPY . .

RUN pip install -r requirements.txt

USER hasker_ad

ENTRYPOINT ["gunicorn","-b","0.0.0.0:8000", "hasker.wsgi:application"]
