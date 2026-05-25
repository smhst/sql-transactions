-- Таблица клиентов
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    signup_date DATE,
    country TEXT,
    credit_score INTEGER
);

-- Таблица карт
CREATE TABLE IF NOT EXISTS cards (
    card_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    card_type TEXT CHECK(card_type IN ('debit','credit')),
    issue_date DATE,
    credit_limit REAL,
    status TEXT DEFAULT 'active'
);

-- Торговые точки
CREATE TABLE IF NOT EXISTS merchants (
    merchant_id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    country TEXT
);

-- Транзакции
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    card_id INTEGER REFERENCES cards(card_id),
    merchant_id INTEGER REFERENCES merchants(merchant_id),
    transaction_date TIMESTAMP,
    amount REAL,
    currency TEXT DEFAULT 'RUB',
    status TEXT CHECK(status IN ('approved','declined','pending','reversed')),
    fraud_flag INTEGER DEFAULT 0
);
