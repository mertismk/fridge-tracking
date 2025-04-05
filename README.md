# Fridge Tracking dhjhjdjgkj

Приложение для отслеживания продуктов в холодильнике.

## Запуск с Docker

### Предварительные требования
- Docker Desktop установлен на вашем компьютере

### Первый запуск

1. Остановите и удалите все существующие Docker контейнеры (если нужно):
```bash
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
```

2. Удалите все Docker образы, если нужно начать с чистого состояния:
```bash
docker rmi $(docker images -q)
```

3. Удалите предыдущие тома базы данных (если есть):
```bash
docker volume prune -f
```

4. Запустите приложение с Docker Compose:
```bash
docker-compose up -d --build
```

5. Проверьте логи, чтобы убедиться, что всё запустилось правильно:
```bash
docker-compose logs -f
```

6. Приложение будет доступно по адресу: http://localhost:5000

### Перезапуск после изменений

Если вы внесли изменения в код:
```bash
docker-compose down
docker-compose up -d --build
```

### Остановка приложения

```bash
docker-compose down
```

## База данных

PostgreSQL база данных будет автоматически инициализирована при первом запуске. Данные будут сохраняться между запусками в Docker volume.

## Вход в систему

Логин администратора: `admin`
Email: `admin@example.com` 
