# Organizations Directory API

REST API для справочника организаций, зданий и деятельности.

## Установка

```bash
git clone https://github.com/NeemThatSearched/Test-Secunda
cd Test-Secunda
./start.sh
```

## API ключ

По умолчанию: `my_super_secret_api_key_2024`

## Endpoints

- Organizations: `/api/v1/organizations/`
- Buildings: `/api/v1/buildings/`
- Activities: `/api/v1/activities/`
- Docs: `/docs` / `/redoc`

## Настройка GitHub Actions

### Обязательные секреты (если нужен деплой на сервер):
API_KEY: "your_secret_api_key"
SECRET_KEY: "your_secret_key"
DEPLOY_HOST: "your-server-ip" 
DEPLOY_USER: "your-username"
DEPLOY_KEY: "-----BEGIN PRIVATE KEY----- ..."

## Тестирование

```bash
python tests/test_api.py
```

## Пример запроса

```bash
curl -H "Authorization: Bearer my_super_secret_api_key_2024" \
  http://localhost:8000/api/v1/organizations/
```

## Технологии

- FastAPI + SQLAlchemy + Alembic + Pydantic
