#!/bin/bash
set -e

# Ожидаем доступности PostgreSQL
wait-for-it.sh db:5432 -t 60

# Запускаем приложение
python run.py 