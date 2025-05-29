# Поднять контейнеры (в фоне)
up:
	docker compose up -d

# Остановить контейнеры
down:
	docker compose down

# Пересобрать образы и запустить
rebuild:
	docker compose down
	docker compose build
	docker compose up -d

logbot:
	docker compose logs bot


dropdb:
	docker compose exec bot_postgres psql -U postgres -c "DROP DATABASE IF EXISTS telegram_mai_students;"

createdb:
	docker compose exec bot_postgres psql -U postgres -c "CREATE DATABASE telegram_mai_students;"

recreatedb: dropdb createdb


fullmigrate: makemigration migrate

# Выполнить миграции
migrate:
	docker compose run --rm bot alembic upgrade head

# Создать миграцию
makemigration:
	docker compose run --rm bot alembic revision --autogenerate


# Очистить volume'ы и образы
prune:
	docker system prune -af --volumes
