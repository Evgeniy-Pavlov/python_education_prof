start:
	python3 manage.py runserver

migrate:
	python3 manage.py makemigrations
	python3 manage.py migrate

activate:
	source ./venv/bin/activate

setup: requirements.txt
    pip install -r requirements.txt

docker-build:
	docker build .

prod:
	docker-compose up

test:
	python3 manage.py test

user:
	python3 manage.py createsuperuser




.PHONY : start migrate activate install docker-start sort black test shell static