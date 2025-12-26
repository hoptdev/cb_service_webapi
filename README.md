Запуск происходит через Docker:  
Команда: docker compose up --build  

Проект включает в себя:  
db - База данных Postgres  
cb_service - Основной сервис, здесь парсер ЦБ + триггер NATS/Сокетов. По умолачанию слушает 8000 порт.  
nats_checker - Демонстрация работоспособности NATS, просто логгер сообщений в NATS  
nats - сам контейнер с NATS  
  
Swagger доступен по пути http://localhost:8000/docs  
