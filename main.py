import os
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def get_connection():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"Database not found {DB_PATH} ")

    return sqlite3.connect(DB_PATH)

def load_customers_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                cpii.customer_id
                , cpii.phone
                , cpii.national_id
                , cpii.card_last4
                , cpii.full_address
                , c.first_name
                , c.last_name
                , c.email
                , c.gender
                , c.birth_date
                , c.city
                , c.country
                , c.segment
                , c.signup_date
            FROM customers c
            JOIN customer_pii cpii ON c.customer_id = cpii.customer_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_products_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                p.product_id
                , p.name AS product
                , c.name AS category
                , s.name AS supplier
                , s.country
                , s.rating
                , p.price
                , p.cost
                , p.is_active
            FROM products p
            JOIN categories c ON c.category_id = p.category_id
            JOIN suppliers s ON s.supplier_id = p.supplier_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_returns_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                r.return_id
                , r.order_id
                , r.reason
                , r.return_date
                , r.refund_amount
            FROM returns r
            """
    df = pd.read_sql_query(query, conn)
    return df 

def load_employees_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                e.employee_id
                , e.first_name
                , e.last_name
                , e.title
                , e.region
                , e.hire_date
                , e.manager_id
                , es.base_salary
                , es.bonus
                , es.currency
            FROM employees e
            JOIN employee_salaries es ON es.employee_id = e.employee_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_orders_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                order_id
                , o.order_date
                , o.customer_id
                , o.employee_id
                , o.status
                , o.ship_country
                , o.ship_city
            FROM orders o
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_inventory_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                i.inventory_id
                , i.product_id
                , w.name
                , w.city
                , w.country
                , i.quantity
            FROM inventory i
            JOIN warehouses w ON w.warehouse_id = i.warehouse_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_shipments_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                s.shipment_id
                , s.order_id
                , s.shipped_date
                , s.delivered_date
                , s.cost
                , sh.name
                , sh.country
            FROM shipments s
            JOIN shippers sh ON sh.shipper_id = s.shipper_id
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_reviews_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                r.review_id
                , r.product_id
                , r.customer_id
                , r.rating
                , r.review_date
            FROM reviews r
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_payments_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                p.payment_id
                , p.order_id
                , p.method
                , p.amount
                , p.paid_at
            FROM payments p
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_promotions_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT
                promotion_id
                , name AS promotion
                , discount_pct AS discount_pct_pr
            FROM promotions
            """
    df = pd.read_sql_query(query, conn)
    return df

def load_order_items_to_df(conn) -> pd.DataFrame:
    query = """
            SELECT 
                oi.order_item_id
                , oi.order_id
                , oi.product_id
                , oi.quantity
                , oi.unit_price
                , oi.discount
                , p.name as promotion
                , p.discount_pct
                , p.start_date
                , p.end_date
            FROM order_items oi
            LEFT JOIN promotions p ON p.promotion_id = oi.promotion_id
            """
    df = pd.read_sql_query(query, conn)
    return df


HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(HERE, 'online_store.db')
connect = get_connection()

customers = load_customers_to_df(connect)
# print(customers.head(5))

products = load_products_to_df(connect)
# print(products.head(5))

employees = load_employees_to_df(connect)
# print(employees.head(5))

orders = load_orders_to_df(connect)
# print(orders.head(5))

returns = load_returns_to_df(connect)
# print(returns.head(5))

inventory = load_inventory_to_df(connect)
# print(inventory.head(5))

shipments = load_shipments_to_df(connect)
# print(shipments.head(5))

reviews = load_reviews_to_df(connect)
# print(reviews.head(5))

payments = load_payments_to_df(connect)
# print(payments.head(5))

order_items = load_order_items_to_df(connect)
# print(order_items.head(5))


# customers.info()
customers['email'] = customers['email'].fillna('no_data')
customers['card_last4'] = customers['card_last4'].astype(int)
customers['signup_date'] = pd.to_datetime(customers['signup_date'])
customers['birth_date'] = pd.to_datetime(customers['birth_date'])
customers['gender'] = customers['gender'].str.lower().replace('','no_data')
customers['city'] = customers['city'].str.strip().str.capitalize() 

country_mapping = {
    'poland': 'PL', 'polska': 'PL', 'pl': 'PL',
    'united kingdom': 'UK', 'u.k.': 'UK', 'uk': 'UK', 'britain': 'UK',
    'united states': 'US', 'u.s.a.': 'US', 'usa': 'US', 'us': 'US',
    'germany': 'DE', 'deutschland': 'DE', 'de': 'DE',
    'france': 'FR', 'fr': 'FR',
    'spain': 'ES', 'españa': 'ES', 'es': 'ES',
    'italy': 'IT', 'italia': 'IT', 'it': 'IT'
}
customers['country'] = customers['country'].str.strip().str.replace(country_mapping)

promotions = load_promotions_to_df(connect)
