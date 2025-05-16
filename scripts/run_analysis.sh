#!/bin/bash

# set -e 

mkdir -p reports

EXIT_CODE=0

echo "-------------------------------------"
echo " Запуск Flake8 для проверки качества кода..."
echo "-------------------------------------"
flake8 .
FLAKE8_EXIT_CODE=$?
if [ $FLAKE8_EXIT_CODE -ne 0 ]; then
    echo "*** Flake8 ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $FLAKE8_EXIT_CODE) ***"
    EXIT_CODE=1
else
    echo "Flake8 прошел успешно."
fi

echo "-------------------------------------"
echo " Запуск Bandit для проверки безопасности..."
echo "-------------------------------------"
bandit -r . -c .bandit.yml -f json -o reports/bandit-report.json
BANDIT_EXIT_CODE=$?
if [ $BANDIT_EXIT_CODE -ne 0 ]; then
    echo "*** Bandit ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $BANDIT_EXIT_CODE) - Проверьте severity/confidence в .bandit.yml ***"
    EXIT_CODE=1
else
    echo "Bandit прошел успешно (не найдено проблем >= high severity)."
fi

echo "-------------------------------------"
echo " Запуск тестов с покрытием..."
echo "-------------------------------------"
# Запуск всех тестов, кроме специально проваливающихся
python -m pytest tests/test_models.py tests/test_utils.py tests/test_routes.py \
    --cov=app --cov-report=xml:reports/coverage.xml --cov-report=term

# Сохраняем код возврата тестов
PYTEST_EXIT_CODE=$?

# Генерируем отчет HTML для покрытия
python -m pytest --cov=app --cov-report=html:reports/coverage_html

# Формируем отчет JUnit XML для Jenkins
python -m pytest --junitxml=reports/pytest_results.xml

if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "*** Pytest ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $PYTEST_EXIT_CODE) ***"
    EXIT_CODE=1
else
    echo "Pytest прошел успешно."
fi

echo "-------------------------------------"
echo " Запуск проверки типов..."
echo "-------------------------------------"
mypy . --txt-report reports/mypy-report.txt
MYPY_EXIT_CODE=$?
if [ $MYPY_EXIT_CODE -ne 0 ]; then
    echo "*** Mypy ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $MYPY_EXIT_CODE), но билд не падает ***"
else
    echo "Mypy прошел успешно."
fi

echo "====================================="
if [ $EXIT_CODE -ne 0 ]; then
    echo "ОБНАРУЖЕНЫ ОШИБКИ АНАЛИЗА! Сборка завершится с ошибкой."
else
    echo "Анализ завершен успешно. Отчеты доступны в директории reports/"
fi
echo "====================================="

exit $EXIT_CODE 