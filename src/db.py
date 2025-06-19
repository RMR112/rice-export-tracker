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

    # Shipments table
    c.execute('''
           CREATE TABLE IF NOT EXISTS shipments (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               container_id TEXT,
               vessel_name TEXT,
               departure_date TEXT,
               status TEXT,
               notes TEXT
           )
       ''')

    # Orders-to-Shipments mapping table (many-to-many)
    c.execute('''
           CREATE TABLE IF NOT EXISTS shipment_orders (
               shipment_id INTEGER,
               order_id INTEGER,
               FOREIGN KEY (shipment_id) REFERENCES shipments(id),
               FOREIGN KEY (order_id) REFERENCES orders(id)
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

def insert_shipment(shipment):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        INSERT INTO shipments (container_id, vessel_name, departure_date, status, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        shipment.container_id,
        shipment.vessel_name,
        shipment.departure_date,
        shipment.status,
        shipment.notes
    ))
    conn.commit()
    conn.close()

def get_shipments():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT * FROM shipments ORDER BY departure_date DESC')
    rows = c.fetchall()
    conn.close()
    return rows

def get_unassigned_orders():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        SELECT id, buyer, variety, quantity_mt FROM orders
        WHERE id NOT IN (SELECT order_id FROM shipment_orders)
    ''')
    result = c.fetchall()
    conn.close()
    return result

def assign_orders_to_shipment(shipment_id, order_ids):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for order_id in order_ids:
        c.execute('INSERT INTO shipment_orders (shipment_id, order_id) VALUES (?, ?)', (shipment_id, order_id))
    conn.commit()
    conn.close()
