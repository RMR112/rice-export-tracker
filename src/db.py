# src/db.py
import sqlite3
from pathlib import Path

DB_PATH = Path("data/rice_export.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            buyer TEXT,
            country TEXT,
            variety TEXT,
            quantity_mt REAL,
            price_per_mt REAL,
            order_date TEXT,
            expected_ship_date TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_order(order):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO orders (buyer, country, variety, quantity_mt, price_per_mt, order_date, expected_ship_date, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        order.buyer,
        order.country,
        order.variety,
        order.quantity_mt,
        order.price_per_mt,
        order.order_date,
        order.expected_ship_date,
        order.notes
    ))
    conn.commit()
    conn.close()

def get_all_orders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM orders ORDER BY order_date DESC")
    rows = c.fetchall()
    conn.close()
    return rows
