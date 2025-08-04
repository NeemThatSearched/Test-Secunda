#!/bin/bash
echo "Запуск API"
if ! docker compose version &> /dev/null; then
    if ! command -v docker-compose &> /dev/null; then
        echo "Docker Compose не установлен или не поддерживается."
        exit 1
    else
        echo "Используется старый docker-compose. Рекомендуется обновить Docker."
        COMPOSE_CMD="docker-compose"
    fi
else
    COMPOSE_CMD="docker compose"
fi



echo "Запуск единого контейнера с встроенным PostgreSQL..."
$COMPOSE_CMD up -d

echo "Ожидание запуска единого контейнера..."
sleep 35

echo "Проверка статуса контейнера..."
$COMPOSE_CMD ps

echo ""
echo "Проверка здоровья приложения..."
sleep 10
curl -s http://localhost:8000/health | grep -q "OK" && echo "✅ Приложение работает!" || echo "⚠️ Приложение еще запускается..."

echo ""
echo "🚀 Приложение запущено!"
echo "📡 API: http://localhost:8000" 
echo "📚 Документация: http://localhost:8000/docs"
echo "🗄️ База данных: PostgreSQL встроенный в контейнер"
echo "🔑 API Key: my_super_secret_api_key_2024"
echo ""
echo "Примеры запросов:"
echo "curl -H \"Authorization: Bearer my_super_secret_api_key_2024\" http://localhost:8000/api/v1/organizations/"
echo ""
echo "Внешний доступ:"
echo "curl -H \"Authorization: Bearer my_super_secret_api_key_2024\" http://$(hostname -I | awk '{print $1}'):8000/api/v1/organizations/"
echo ""
echo "Для остановки: $COMPOSE_CMD down"
echo "Для просмотра логов: $COMPOSE_CMD logs -f"