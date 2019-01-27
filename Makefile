.PHONY: app

migrations:
	docker-compose run --rm app sh -c './manage.py makemigrations'

app:
	docker-compose up app

down:
	docker-compose down

stop:
	docker-compose stop

test:
	docker-compose run --rm app sh -c './manage.py test -v3 && flake8'
