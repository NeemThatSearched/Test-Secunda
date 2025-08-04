#!/bin/bash
echo "=== ЗАПУСК ПРИЛОЖЕНИЯ ==="
service postgresql start
sleep 5
su - postgres -c "createdb organizations_db" || true
su - postgres -c "psql -c \"ALTER USER postgres PASSWORD 'password';\"" || true
su - postgres -c "psql -c \"CREATE USER app_user WITH PASSWORD 'password';\"" || true  
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE organizations_db TO app_user;\"" || true
export DATABASE_URL="postgresql+asyncpg://app_user:password@localhost:5432/organizations_db"
python3 -m alembic upgrade head
python3 scripts/seed_data.py
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000