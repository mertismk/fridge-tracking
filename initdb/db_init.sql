CREATE EXTENSION IF NOT EXISTS citext;

CREATE TABLE IF NOT EXISTS "user" ( 
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    date_joined TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO "user" (username, email, password_hash, date_joined)
VALUES ('admin', 'admin@example.com', 'scrypt:32768:8:1$BGt7VY984drJKydT$a3f4725ee4fd9c6c57cf5e408f203aa1082671e3c78571493da8e0ea6c45d92df14efd11b0f389e68399be99ddc2bd7666a2c0a4994f1156b0505c9bac7e105e', CURRENT_TIMESTAMP);


CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    expiry_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    date_added TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES "user"(id)
);


INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES
    ('Молоко', 'Молочные продукты', 1, 'л', NOW() + INTERVAL '7 days', NOW() - INTERVAL '1 day', 1),
    ('Хлеб', 'Бакалея', 1, 'шт', NOW() + INTERVAL '3 days', NOW(), 1),
    ('Яблоки', 'Фрукты', 0.5, 'кг', NOW() + INTERVAL '10 days', NOW() - INTERVAL '2 days', 1),
    ('Куриное филе', 'Мясо', 0.7, 'кг', NOW() + INTERVAL '2 days', NOW() - INTERVAL '1 day', 1),
    ('Помидоры', 'Овощи', 0.4, 'кг', NOW() + INTERVAL '5 days', NOW(), 1);


INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES
    ('Рыба', 'Мясо', 0.5, 'кг', NOW() + INTERVAL '1 days', NOW() - INTERVAL '2 days', 1),
    ('Творог', 'Молочные продукты', 200, 'г', NOW() + INTERVAL '2 days', NOW() - INTERVAL '3 days', 1);


INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES
    ('Йогурт', 'Молочные продукты', 0.3, 'л', NOW() - INTERVAL '2 days', NOW() - INTERVAL '10 days', 1),
    ('Салат', 'Овощи', 0.2, 'кг', NOW() - INTERVAL '1 days', NOW() - INTERVAL '5 days', 1);


INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
VALUES
    ('Варенье', 'Бакалея', 0.5, 'кг', NOW() + INTERVAL '180 days', NOW() - INTERVAL '45 days', 1),
    ('Замороженные ягоды', 'Замороженные продукты', 0.4, 'кг', NOW() + INTERVAL '90 days', NOW() - INTERVAL '35 days', 1),
    ('Соус соевый', 'Бакалея', 0.2, 'л', NOW() + INTERVAL '120 days', NOW() - INTERVAL '40 days', 1),
    ('Мороженое', 'Замороженные продукты', 0.5, 'кг', NOW() + INTERVAL '45 days', NOW() - INTERVAL '25 days', 1),
    ('Джем', 'Бакалея', 0.3, 'кг', NOW() + INTERVAL '90 days', NOW() - INTERVAL '20 days', 1);