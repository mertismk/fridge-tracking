CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    date_joined TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Вставляем администратора только если его еще нет
INSERT INTO "user" (username, email, password_hash, date_joined)
SELECT 'admin', 'admin@example.com', 'scrypt:32768:8:1$BGt7VY984drJKydT$a3f4725ee4fd9c6c57cf5e408f203aa1082671e3c78571493da8e0ea6c45d92df14efd11b0f389e68399be99ddc2bd7666a2c0a4994f1156b0505c9bac7e105e', CURRENT_TIMESTAMP
WHERE NOT EXISTS (SELECT 1 FROM "user" WHERE username = 'admin');

CREATE TABLE IF NOT EXISTS product (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    quantity FLOAT NOT NULL,
    unit VARCHAR(20) NOT NULL,
    expiry_date TIMESTAMP NOT NULL,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INTEGER REFERENCES "user"(id)
);

-- Вставляем примеры продуктов, только если таблица пуста
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM product LIMIT 1) THEN
        INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
        VALUES 
            ('Молоко', 'Молочные продукты', 1, 'л', CURRENT_DATE + INTERVAL '7 days', CURRENT_DATE - INTERVAL '1 day', 1),
            ('Хлеб', 'Бакалея', 1, 'шт', CURRENT_DATE + INTERVAL '3 days', CURRENT_DATE, 1),
            ('Яблоки', 'Фрукты', 0.5, 'кг', CURRENT_DATE + INTERVAL '10 days', CURRENT_DATE - INTERVAL '2 days', 1),
            ('Куриное филе', 'Мясо', 0.7, 'кг', CURRENT_DATE + INTERVAL '2 days', CURRENT_DATE - INTERVAL '1 day', 1),
            ('Помидоры', 'Овощи', 0.4, 'кг', CURRENT_DATE + INTERVAL '5 days', CURRENT_DATE, 1);

        INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
        VALUES 
            ('Рыба', 'Мясо', 0.5, 'кг', CURRENT_DATE + INTERVAL '1 day', CURRENT_DATE - INTERVAL '2 days', 1),
            ('Творог', 'Молочные продукты', 200, 'г', CURRENT_DATE + INTERVAL '2 days', CURRENT_DATE - INTERVAL '3 days', 1);

        INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
        VALUES 
            ('Йогурт', 'Молочные продукты', 0.3, 'л', CURRENT_DATE - INTERVAL '2 days', CURRENT_DATE - INTERVAL '10 days', 1),
            ('Салат', 'Овощи', 0.2, 'кг', CURRENT_DATE - INTERVAL '1 day', CURRENT_DATE - INTERVAL '5 days', 1);

        INSERT INTO product (name, category, quantity, unit, expiry_date, date_added, user_id)
        VALUES 
            ('Варенье', 'Бакалея', 0.5, 'кг', CURRENT_DATE + INTERVAL '180 days', CURRENT_DATE - INTERVAL '45 days', 1),
            ('Замороженные ягоды', 'Замороженные продукты', 0.4, 'кг', CURRENT_DATE + INTERVAL '90 days', CURRENT_DATE - INTERVAL '35 days', 1),
            ('Соус соевый', 'Бакалея', 0.2, 'л', CURRENT_DATE + INTERVAL '120 days', CURRENT_DATE - INTERVAL '40 days', 1),
            ('Мороженое', 'Замороженные продукты', 0.5, 'кг', CURRENT_DATE + INTERVAL '45 days', CURRENT_DATE - INTERVAL '25 days', 1),
            ('Джем', 'Бакалея', 0.3, 'кг', CURRENT_DATE + INTERVAL '90 days', CURRENT_DATE - INTERVAL '20 days', 1);
    END IF;
END $$;
