.PHONY: app

migrations:
	docker-compose run --rm app sh -c \
	'./manage.py wait_for_db && \
	./manage.py makemigrations'

migrate:
	docker-compose run --rm app sh -c \
	'./manage.py wait_for_db && \
	./manage.py migrate'


app:
	docker-compose up app

down:
	docker-compose down

stop:
	docker-compose stop

test:
	docker-compose run --rm test
