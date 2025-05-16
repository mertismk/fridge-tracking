#!/bin/bash

echo "НАЧАЛО СКРИПТА run_analysis.sh"

mkdir -p reports
echo "Создан каталог reports"

EXIT_CODE=0

echo "-------------------------------------"
echo " ЗАПУСК Flake8 для проверки качества кода..."
echo "-------------------------------------"
flake8 .
FLAKE8_EXIT_CODE=$?
echo "Flake8 ЗАВЕРШЕН с кодом: $FLAKE8_EXIT_CODE"
if [ $FLAKE8_EXIT_CODE -ne 0 ]; then
    echo "*** Flake8 ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $FLAKE8_EXIT_CODE) ***"
    EXIT_CODE=1
# else
#     echo "Flake8 прошел успешно."
fi

echo "-------------------------------------"
echo " ЗАПУСК Bandit для проверки безопасности..."
echo "-------------------------------------"
bandit -r . -c .bandit.yml -f json -o reports/bandit-report.json
BANDIT_EXIT_CODE=$?
echo "Bandit ЗАВЕРШЕН с кодом: $BANDIT_EXIT_CODE"
if [ $BANDIT_EXIT_CODE -ne 0 ]; then
    echo "*** Bandit ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $BANDIT_EXIT_CODE) - Проверьте severity/confidence в .bandit.yml ***"
    EXIT_CODE=1
# else
#     echo "Bandit прошел успешно (не найдено проблем >= high severity)."
fi

echo "-------------------------------------"
echo " ЗАПУСК Pytest с покрытием и JUnit отчетом..."
echo "-------------------------------------"
# Запуск всех тестов, кроме специально проваливающихся
python -m pytest tests/test_models.py tests/test_utils.py tests/test_routes.py \
    --cov=app --cov-report=xml:reports/coverage.xml --cov-report=term --junitxml=reports/pytest_results.xml

PYTEST_EXIT_CODE=$?
echo "Pytest (основной) ЗАВЕРШЕН с кодом: $PYTEST_EXIT_CODE"

echo "-------------------------------------"
echo " ЗАПУСК Pytest для генерации HTML отчета о покрытии..."
echo "-------------------------------------"
# Генерируем отчет HTML для покрытия
# Эту команду можно объединить с предыдущей, но для отладки разделим
python -m pytest --cov=app --cov-report=html:reports/coverage_html tests/test_models.py tests/test_utils.py tests/test_routes.py
PYTEST_HTML_EXIT_CODE=$?
echo "Pytest (HTML отчет) ЗАВЕРШЕН с кодом: $PYTEST_HTML_EXIT_CODE"

echo "-------------------------------------"
echo " ДЕБАГ: Проверка созданных отчетов..."
echo "-------------------------------------"
echo "ДЕБАГ: Содержимое каталога /app/reports:"
ls -lR /app/reports
echo "-------------------------------------"
echo "ДЕБАГ: Содержимое /app/reports/pytest_results.xml (если существует):"
if [ -f /app/reports/pytest_results.xml ]; then
    echo "ДЕБАГ: Файл /app/reports/pytest_results.xml НАЙДЕН. Содержимое:"
    cat /app/reports/pytest_results.xml
else
    echo "ДЕБАГ: Файл /app/reports/pytest_results.xml НЕ НАЙДЕН."
fi
echo "-------------------------------------"
echo "ДЕБАГ: Проверка существования /app/reports/coverage_html:"
if [ -d /app/reports/coverage_html ]; then
    echo "ДЕБАГ: Каталог /app/reports/coverage_html СУЩЕСТВУЕТ."
    echo "ДЕБАГ: Содержимое /app/reports/coverage_html:"
    ls -lR /app/reports/coverage_html
else
    echo "ДЕБАГ: Каталог /app/reports/coverage_html НЕ НАЙДЕН."
fi
echo "-------------------------------------"


if [ $PYTEST_EXIT_CODE -ne 0 ] || [ $PYTEST_HTML_EXIT_CODE -ne 0 ]; then
    echo "*** Pytest ЗАВЕРШИЛСЯ С ОШИБКОЙ (коды: основной=$PYTEST_EXIT_CODE, HTML=$PYTEST_HTML_EXIT_CODE) ***"
    EXIT_CODE=1
# else
#     echo "Pytest прошел успешно."
fi

echo "-------------------------------------"
echo " ЗАПУСК Mypy для проверки типов..."
echo "-------------------------------------"
mypy . --txt-report reports/mypy-report.txt
MYPY_EXIT_CODE=$?
echo "Mypy ЗАВЕРШЕН с кодом: $MYPY_EXIT_CODE"
if [ $MYPY_EXIT_CODE -ne 0 ]; then
    echo "*** Mypy ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $MYPY_EXIT_CODE), но билд не падает ***"
# else
#     echo "Mypy прошел успешно."
fi

echo "====================================="
if [ $EXIT_CODE -ne 0 ]; then
    echo "ОБНАРУЖЕНЫ ОШИБКИ АНАЛИЗА! Сборка завершится с ошибкой."
else
    echo "Анализ завершен успешно. Отчеты доступны в директории reports/"
fi
echo "====================================="
echo "КОНЕЦ СКРИПТА run_analysis.sh. Код возврата: $EXIT_CODE"
exit $EXIT_CODE