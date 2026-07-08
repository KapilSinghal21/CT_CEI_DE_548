"""
load_db.py
Creates the SQLite database from sql/schema.sql and loads the cleaned CSVs.
"""

import sqlite3
import csv

DB_PATH = "ecommerce.db"
SCHEMA_PATH = "sql/schema.sql"
CLEAN_DIR = "data/cleaned"


def create_schema(conn):
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())


def load_csv(conn, table, path, columns):
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append(tuple(row[c] if row[c] != "" else None for c in columns))
    placeholders = ", ".join(["?"] * len(columns))
    col_list = ", ".join(columns)
    conn.executemany(f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})", rows)
    print(f"Loaded {len(rows)} rows into {table}")


def main():
    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)

    load_csv(conn, "customers", f"{CLEAN_DIR}/customers_clean.csv",
             ["customer_id", "customer_name", "email", "registration_date", "customer_type"])
    load_csv(conn, "products", f"{CLEAN_DIR}/products_clean.csv",
             ["product_id", "product_name", "category", "subcategory", "cost_price"])
    load_csv(conn, "orders", f"{CLEAN_DIR}/orders_clean.csv",
             ["order_id", "customer_id", "order_date", "status", "region_code"])
    load_csv(conn, "order_items", f"{CLEAN_DIR}/order_items_clean.csv",
             ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])

    conn.commit()

    # Verify counts
    for table in ["customers", "products", "orders", "order_items"]:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table}: {cnt} rows in DB")

    conn.close()


if __name__ == "__main__":
    main()
