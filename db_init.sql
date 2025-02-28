-- Создание таблицы пользователей
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Вставка пользователя admin
-- Для поля password_hash необходимо использовать хеш пароля, сгенерированный, например, так:
-- >>> from werkzeug.security import generate_password_hash
-- >>> print(generate_password_hash("admin"))
-- Скопируйте полученную строку сюда.
INSERT INTO user (username, email, password_hash, date_joined)
VALUES ('admin', 'admin@example.com', 'scrypt:32768:8:1$BGt7VY984drJKydT$a3f4725ee4fd9c6c57cf5e408f203aa1082671e3c78571493da8e0ea6c45d92df14efd11b0f389e68399be99ddc2bd7666a2c0a4994f1156b0505c9bac7e105e', CURRENT_TIMESTAMP);

-- Создание таблицы продуктов с внешним ключом user_id
CREATE TABLE IF NOT EXISTS product (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    expiry_date DATETIME NOT NULL,
    date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

-- Вставка тестовых данных для продуктов с привязкой к admin (user_id = 1)
-- Убедитесь, что пользователь admin имеет id = 1 (он будет первым пользователем).
INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES 
    ('Молоко', 'Молочные продукты', 1, 'л', date('now', '+7 days'), date('now', '-1 days'), 1),
    ('Хлеб', 'Бакалея', 1, 'шт', date('now', '+3 days'), date('now'), 1),
    ('Яблоки', 'Фрукты', 0.5, 'кг', date('now', '+10 days'), date('now', '-2 days'), 1),
    ('Куриное филе', 'Мясо', 0.7, 'кг', date('now', '+2 days'), date('now', '-1 days'), 1),
    ('Помидоры', 'Овощи', 0.4, 'кг', date('now', '+5 days'), date('now'), 1);

-- Продукты, которые скоро испортятся
INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES 
    ('Рыба', 'Мясо', 0.5, 'кг', date('now', '+1 days'), date('now', '-2 days'), 1),
    ('Творог', 'Молочные продукты', 200, 'г', date('now', '+2 days'), date('now', '-3 days'), 1);

-- Просроченные продукты
INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES 
    ('Йогурт', 'Молочные продукты', 0.3, 'л', date('now', '-2 days'), date('now', '-10 days'), 1),
    ('Салат', 'Овощи', 0.2, 'кг', date('now', '-1 days'), date('now', '-5 days'), 1);

-- "Долгожители" - ветераны холодильника
INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES 
    ('Варенье', 'Бакалея', 0.5, 'кг', date('now', '+180 days'), date('now', '-45 days'), 1),
    ('Замороженные ягоды', 'Замороженные продукты', 0.4, 'кг', date('now', '+90 days'), date('now', '-35 days'), 1),
    ('Соус соевый', 'Бакалея', 0.2, 'л', date('now', '+120 days'), date('now', '-40 days'), 1),
    ('Мороженое', 'Замороженные продукты', 0.5, 'кг', date('now', '+45 days'), date('now', '-25 days'), 1),
    ('Джем', 'Бакалея', 0.3, 'кг', date('now', '+90 days'), date('now', '-20 days'), 1);
