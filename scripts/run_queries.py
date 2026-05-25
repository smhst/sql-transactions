import sqlite3
import pandas as pd
import os

DB_PATH = 'data/transactions.db'
QUERIES_DIR = 'sql/02_queries'
OUTPUT_DIR = 'output/reports'

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

for filename in sorted(os.listdir(QUERIES_DIR)):
    if filename.endswith('.sql'):
        filepath = os.path.join(QUERIES_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            query = f.read()
        print(f"Выполняется: {filename}")
        try:
            df = pd.read_sql_query(query, conn)
            # Сохраняем в CSV
            out_name = filename.replace('.sql', '.csv')
            out_path = os.path.join(OUTPUT_DIR, out_name)
            df.to_csv(out_path, index=False)
            print(f"  -> сохранён {out_path} ({len(df)} строк)")
        except Exception as e:
            print(f"  Ошибка: {e}")

conn.close()
print("Готово.")
