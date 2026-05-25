import sqlite3
import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

# Инициализация Faker с русской локалью (имена городов, имена людей будут русскими)
fake = Faker('ru_RU')
# Фиксируем seed для воспроизводимости случайных данных
np.random.seed(42)
random.seed(42)
Faker.seed(42)

# Параметры генерации
NUM_CUSTOMERS = 500      # клиентов
NUM_CARDS = 600           # карт (у некоторых клиентов >1)
NUM_MERCHANTS = 150       # торговых точек
NUM_TRANSACTIONS = 30000  # транзакций
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2024, 12, 31)

print("Генерирую клиентов...")
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    customers.append({
        'customer_id': i,
        'first_name': fake.first_name(),
        'last_name': fake.last_name(),
        'email': fake.email(),
        'signup_date': fake.date_between(start_date='-3y', end_date='-1d'),
        'country': 'Russia',   # для упрощения, можно fake.country()
        'credit_score': np.random.randint(300, 850)
    })
df_customers = pd.DataFrame(customers)

print("Генерирую карты...")
cards = []
card_types = ['debit', 'credit']
for i in range(1, NUM_CARDS + 1):
    cust_id = np.random.randint(1, NUM_CUSTOMERS + 1)
    c_type = random.choice(card_types)
    cards.append({
        'card_id': i,
        'customer_id': cust_id,
        'card_type': c_type,
        'issue_date': fake.date_between(start_date='-2y', end_date='-1m'),
        'credit_limit': round(np.random.uniform(10000, 300000), 2) if c_type == 'credit' else 0,
        'status': 'active'
    })
df_cards = pd.DataFrame(cards)

print("Генерирую торговые точки...")
merchants = []
categories = ['supermarket', 'cafe', 'electronics', 'clothing', 'pharmacy', 'transport', 'fuel', 'restaurant', 'entertainment', 'utilities']
for i in range(1, NUM_MERCHANTS + 1):
    merchants.append({
        'merchant_id': i,
        'name': fake.company(),
        'category': random.choice(categories),
        'country': 'Russia'  # почти всегда Россия, добавим несколько иностранных позже для фрода
    })
# Добавим несколько зарубежных
for i in range(NUM_MERCHANTS + 1, NUM_MERCHANTS + 6):
    merchants.append({
        'merchant_id': i,
        'name': fake.company(),
        'category': random.choice(categories),
        'country': fake.country()
    })
df_merchants = pd.DataFrame(merchants)

print("Генерирую транзакции...")
transactions = []
statuses = ['approved', 'declined', 'pending']
# Небольшой процент fraud-транзакций добавим позже
for i in range(1, NUM_TRANSACTIONS + 1):
    card_id = np.random.randint(1, NUM_CARDS + 1)
    merchant_id = np.random.randint(1, len(df_merchants) + 1)
    # Дата и время случайные в пределах года
    rand_seconds = np.random.randint(0, int((END_DATE - START_DATE).total_seconds()))
    tx_date = START_DATE + timedelta(seconds=rand_seconds)
    # Сумма: большинство до 10 000, но есть крупные
    if np.random.random() < 0.8:
        amount = round(np.random.uniform(10, 5000), 2)
    else:
        amount = round(np.random.uniform(5001, 150000), 2)
    status = random.choice(statuses)
    transactions.append({
        'transaction_id': i,
        'card_id': card_id,
        'merchant_id': merchant_id,
        'transaction_date': tx_date.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': amount,
        'currency': 'RUB',
        'status': status,
        'fraud_flag': 0
    })
df_transactions = pd.DataFrame(transactions)

# Вставим искусственные fraud-паттерны (ночные большие суммы или в другой стране)
# Сделаем примерно 0.5% транзакций подозрительными
fraud_indices = np.random.choice(df_transactions.index, size=int(NUM_TRANSACTIONS * 0.005), replace=False)
for idx in fraud_indices:
    # Изменим время на ночное
    old_date = datetime.strptime(df_transactions.at[idx, 'transaction_date'], '%Y-%m-%d %H:%M:%S')
    new_date = old_date.replace(hour=np.random.randint(0, 5), minute=np.random.randint(0, 60))
    df_transactions.at[idx, 'transaction_date'] = new_date.strftime('%Y-%m-%d %H:%M:%S')
    df_transactions.at[idx, 'amount'] = round(np.random.uniform(80000, 200000), 2)
    # Поменяем merchant на зарубежный (id >= NUM_MERCHANTS+1)
    df_transactions.at[idx, 'merchant_id'] = np.random.randint(NUM_MERCHANTS + 1, len(df_merchants) + 1)
    df_transactions.at[idx, 'fraud_flag'] = 1

# Сохраняем в SQLite
conn = sqlite3.connect('data/transactions.db')
print("Сохраняю таблицы в базу данных...")
df_customers.to_sql('customers', conn, if_exists='replace', index=False)
df_cards.to_sql('cards', conn, if_exists='replace', index=False)
df_merchants.to_sql('merchants', conn, if_exists='replace', index=False)
df_transactions.to_sql('transactions', conn, if_exists='replace', index=False)

# Создаём индексы для ускорения запросов
conn.execute('CREATE INDEX IF NOT EXISTS idx_trans_card ON transactions(card_id)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_trans_merchant ON transactions(merchant_id)')
conn.execute('CREATE INDEX IF NOT EXISTS idx_trans_date ON transactions(transaction_date)')
conn.commit()
conn.close()

print("Генерация завершена. База данных: data/transactions.db")
