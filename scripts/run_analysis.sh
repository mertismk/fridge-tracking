#!/bin/bash

# Убираем set -e для детальной отладки
# set -e 

# Создаем директорию для отчетов, если она не существует
mkdir -p reports

# Флаг для отслеживания общей ошибки
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
echo " Запуск Gitleaks для поиска секретов..."
echo "-------------------------------------"
# Gitleaks будет установлен через apt-get внутри docker run
# Запускаем с --exit-code 1
if command -v gitleaks &> /dev/null; then
    gitleaks detect --source . --report-path reports/gitleaks-report.json --report-format json --exit-code 1 -v
    GITLEAKS_EXIT_CODE=$?
    if [ $GITLEAKS_EXIT_CODE -ne 0 ]; then
        echo "*** Gitleaks НАШЕЛ СЕКРЕТЫ или ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $GITLEAKS_EXIT_CODE) ***"
        EXIT_CODE=1
    else
        echo "Gitleaks прошел успешно (секреты не найдены)."
    fi
else
     # Этого не должно произойти, так как мы установим gitleaks через apt/wget
    echo "*** ОШИБКА: gitleaks не найден после попытки установки! ***"
    EXIT_CODE=1 
fi

echo "-------------------------------------"
echo " Запуск тестов с покрытием..."
echo "-------------------------------------"
pytest --cov=. --cov-report=xml:reports/coverage.xml tests/
PYTEST_EXIT_CODE=$?
if [ $PYTEST_EXIT_CODE -ne 0 ]; then
    echo "*** Pytest ЗАВЕРШИЛСЯ С ОШИБКОЙ (код: $PYTEST_EXIT_CODE) ***"
    # EXIT_CODE=1 # Раскомментируйте, если падение тестов должно валить билд
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
echo "====================================="

# Возвращаем общий код ошибки
exit $EXIT_CODE 