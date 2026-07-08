"""
generate_data.py
Generates 4 raw CSV files with realistic but intentionally messy e-commerce data:
customers.csv, products.csv, orders.csv, order_items.csv

Intentional issues introduced:
- 5% of orders have NULL customer_id
- 3% of order_items have negative quantity (returns)
- Some orders have order_date in DD-MM-YYYY format instead of YYYY-MM-DD HH:MM:SS
- Some product names have extra spaces / mixed case
- 2% of emails are invalid (missing @ or domain)
- order_items.order_id always references a real orders.order_id (referential integrity by construction)
"""

import csv
import random
from datetime import datetime, timedelta

random.seed(42)

OUT_DIR = "data/raw"

FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan",
               "Ananya", "Diya", "Ishaan", "Kabir", "Priya", "Riya", "Saanvi", "Anaya",
               "Rohan", "Karan", "Neha", "Pooja", "Amit", "Sneha", "Rahul", "Nisha"]
LAST_NAMES = ["Sharma", "Verma", "Gupta", "Singh", "Kumar", "Patel", "Reddy", "Nair",
              "Iyer", "Menon", "Chopra", "Malhotra", "Rao", "Joshi", "Desai", "Kapoor"]

CATEGORIES = {
    "Electronics": ["Smartphone", "Laptop", "Headphones", "Smartwatch", "Tablet", "Speaker", "Camera"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sweater", "Shoes", "Cap"],
    "Home": ["Blender", "Vacuum Cleaner", "Lamp", "Cookware Set", "Bedsheet", "Curtains", "Chair"],
    "Books": ["Novel", "Cookbook", "Biography", "Self-Help Book", "Comic", "Textbook", "Journal"],
}

CUSTOMER_TYPES = ["REGULAR", "PREMIUM", "VIP"]
ORDER_STATUSES = ["PLACED", "SHIPPED", "DELIVERED", "CANCELLED", "RETURNED"]
REGION_CODES = ["NORTH", "SOUTH", "EAST", "WEST", "CENTRAL"]

N_CUSTOMERS = 550
N_PRODUCTS = 120
N_ORDERS = 1200
N_ORDER_ITEMS = 2600


def random_date(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def messy_email(name, idx, make_invalid):
    base = name.lower().replace(" ", ".")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    if make_invalid:
        choice = random.choice(["no_at", "no_domain"])
        if choice == "no_at":
            return f"{base}{idx}gmail.com"
        else:
            return f"{base}{idx}@"
    return f"{base}{idx}@{random.choice(domains)}"


def generate_customers():
    rows = []
    for i in range(1, N_CUSTOMERS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        invalid_email = random.random() < 0.02
        email = messy_email(name, i, invalid_email)
        reg_date = random_date(datetime(2022, 1, 1), datetime(2025, 12, 31))
        rows.append({
            "customer_id": i,
            "customer_name": name,
            "email": email,
            "registration_date": reg_date.strftime("%Y-%m-%d"),
            "customer_type": random.choices(CUSTOMER_TYPES, weights=[0.6, 0.3, 0.1])[0],
        })
    return rows


def generate_products():
    rows = []
    pid = 1
    for category, names in CATEGORIES.items():
        for _ in range(N_PRODUCTS // len(CATEGORIES)):
            base_name = random.choice(names)
            subcat = f"{category} - {base_name}"
            name = f"{base_name} Model {random.randint(1, 20)}"
            # Introduce messiness: extra spaces / mixed case
            if random.random() < 0.25:
                name = "  " + name.upper() + "  "
            elif random.random() < 0.25:
                name = name.lower()
            cost_price = round(random.uniform(5, 800), 2)
            rows.append({
                "product_id": pid,
                "product_name": name,
                "category": category,
                "subcategory": subcat,
                "cost_price": cost_price,
            })
            pid += 1
    return rows


def generate_orders(customer_ids):
    rows = []
    for i in range(1, N_ORDERS + 1):
        make_null_customer = random.random() < 0.05
        customer_id = "" if make_null_customer else random.choice(customer_ids)
        order_dt = random_date(datetime(2024, 1, 1), datetime(2025, 12, 31))
        wrong_format = random.random() < 0.10
        if wrong_format:
            order_date_str = order_dt.strftime("%d-%m-%Y")
        else:
            order_date_str = order_dt.strftime("%Y-%m-%d %H:%M:%S")
        status = random.choices(
            ORDER_STATUSES, weights=[0.15, 0.15, 0.5, 0.1, 0.1]
        )[0]
        rows.append({
            "order_id": i,
            "customer_id": customer_id,
            "order_date": order_date_str,
            "status": status,
            "region_code": random.choice(REGION_CODES),
        })
    return rows


def generate_order_items(order_ids, product_ids):
    rows = []
    for i in range(1, N_ORDER_ITEMS + 1):
        order_id = random.choice(order_ids)
        product_id = random.choice(product_ids)
        negative_qty = random.random() < 0.03
        quantity = -random.randint(1, 3) if negative_qty else random.randint(1, 5)
        unit_price = round(random.uniform(5, 900), 2)
        discount_percent = round(random.uniform(0, 100), 1) if random.random() < 0.3 else round(random.uniform(0, 30), 1)
        rows.append({
            "item_id": i,
            "order_id": order_id,
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": unit_price,
            "discount_percent": discount_percent,
        })
    return rows


def write_csv(rows, filename, fieldnames):
    path = f"{OUT_DIR}/{filename}"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows -> {path}")


def main():
    customers = generate_customers()
    products = generate_products()
    orders = generate_orders([c["customer_id"] for c in customers])
    order_items = generate_order_items(
        [o["order_id"] for o in orders],
        [p["product_id"] for p in products],
    )

    write_csv(customers, "customers.csv",
              ["customer_id", "customer_name", "email", "registration_date", "customer_type"])
    write_csv(products, "products.csv",
              ["product_id", "product_name", "category", "subcategory", "cost_price"])
    write_csv(orders, "orders.csv",
              ["order_id", "customer_id", "order_date", "status", "region_code"])
    write_csv(order_items, "order_items.csv",
              ["item_id", "order_id", "product_id", "quantity", "unit_price", "discount_percent"])


if __name__ == "__main__":
    main()
