#!/bin/bash

# Создаем директорию для отчетов, если она не существует
mkdir -p reports

# Запускаем Bandit для проверки безопасности
echo "Запуск Bandit для проверки безопасности..."
bandit -r . -c .bandit.yml -f json -o bandit-report.json

# Запускаем тесты с покрытием
echo "Запуск тестов с покрытием..."
pytest --cov=. --cov-report=xml:coverage.xml tests/

# Запускаем проверку типов
echo "Запуск проверки типов..."
mypy . --txt-report reports/mypy

echo "Анализ завершен. Отчеты доступны в директории reports/" 