# Используем готовый FastAPI образ от tiangolo
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

# Копируем весь проект
COPY . /app

RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/* || echo "PostgreSQL клиент не установлен - сетевые проблемы"

# Настраиваем переменные окружения для приложения
ENV MODULE_NAME=app.main
ENV VARIABLE_NAME=app
ENV WORKERS_PER_CORE=1
ENV MAX_WORKERS=1
ENV LOG_LEVEL=info
ENV DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/organizations_db

EXPOSE 80