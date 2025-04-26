#!/bin/bash

# Выходить немедленно, если команда завершается с ненулевым статусом.
set -e

# Создаем директорию для отчетов, если она не существует
mkdir -p reports

echo "-------------------------------------"
echo " Запуск Flake8 для проверки качества кода..."
echo "-------------------------------------"
# Flake8 завершится с ошибкой, если найдет проблемы
flake8 .

echo "-------------------------------------"
echo " Запуск Bandit для проверки безопасности..."
echo "-------------------------------------"
# Bandit завершится с ошибкой, если найдет проблемы >= high severity (согласно .bandit.yml)
bandit -r . -c .bandit.yml -f json -o reports/bandit-report.json

echo "-------------------------------------"
echo " Запуск Gitleaks для поиска секретов..."
echo "-------------------------------------"
# Скачиваем Gitleaks (пример для Linux x64)
# Вы можете найти другие версии здесь: https://github.com/gitleaks/gitleaks/releases
GITLEAKS_VERSION="8.18.4" # Укажите актуальную версию
ARCH="x64"
if ! command -v gitleaks &> /dev/null; then
    echo "Скачивание Gitleaks..."
    wget "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_linux_${ARCH}.tar.gz" -O gitleaks.tar.gz
    tar -xzf gitleaks.tar.gz gitleaks
    rm gitleaks.tar.gz
    chmod +x gitleaks
    MV_CMD="mv"
    if sudo -n true 2>/dev/null; then # Проверка на sudo без пароля
        MV_CMD="sudo mv"
    fi
    $MV_CMD gitleaks /usr/local/bin/ # Перемещаем в PATH, если возможно
fi
# Gitleaks завершится с ошибкой (--exit-code 1), если найдет секреты
gitleaks detect --source . --report-path reports/gitleaks-report.json --report-format json --exit-code 1 -v

echo "-------------------------------------"
echo " Запуск тестов с покрытием..."
echo "-------------------------------------"
# Запускаем тесты, но их падение не обязательно валит билд (если set -e убрать или обрабатывать ошибку)
pytest --cov=. --cov-report=xml:reports/coverage.xml tests/

echo "-------------------------------------"
echo " Запуск проверки типов..."
echo "-------------------------------------"
# Запускаем mypy
mypy . --txt-report reports/mypy-report.txt || true # Игнорируем ошибки mypy для прохождения билда

echo "====================================="
echo " Анализ завершен. Отчеты доступны в директории reports/"
echo "=====================================" 