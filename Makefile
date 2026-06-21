DC = docker compose
APP_SERVICE = app


.PHONY: app # Запуск контейнеров
app:
	$(DC) up -d


.PHONY: down # Остановка контейнеров
down:
	$(DC) down


.PHONY: migrate # Миграция базы данных
migrate:
	$(DC) exec $(APP_SERVICE) alembic upgrade head
