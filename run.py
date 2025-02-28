# run.py
from app import create_app, db
import sqlite3
import os

app = create_app()

def init_db():
    """Инициализация базы данных с тестовыми данными если она не существует"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'fridge_planner.db')
    
    # Проверяем, существует ли база данных
    if not os.path.exists(db_path):
        # Создаем директорию для БД, если она не существует
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        print("Создание новой базы данных с тестовыми данными...")
        
        # Читаем SQL-скрипт
        sql_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db_init.sql')
        
        if os.path.exists(sql_path):
            with open(sql_path, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Создаем БД и выполняем скрипт
            conn = sqlite3.connect(db_path)
            conn.executescript(sql_script)
            conn.commit()
            conn.close()
            
            print("База данных успешно инициализирована!")
        else:
            print("Файл db_init.sql не найден!")
            # Создаем таблицы через SQLAlchemy
            with app.app_context():
                db.create_all()
                print("Таблицы созданы через SQLAlchemy")
    else:
        print("База данных уже существует")

if __name__ == '__main__':
    # Инициализация базы данных
    init_db()
    
    # Запуск приложения
    app.run(debug=True)