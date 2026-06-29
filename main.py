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


#2.6 -------------------------------------------------------------------------------------------
#Проаналізувати зміну середнього рейтингу за період 2022–2026
orders_full = order_items.merge(products, on='product_id', how='inner')
orders_full = orders_full.merge(orders, on='order_id', how='inner')
orders_full['order_date'] = pd.to_datetime(orders_full['order_date'])
orders_full['year'] = orders_full['order_date'].dt.year
orders_full['month'] = orders_full['order_date'].dt.month
mean_rating_year = orders_full.groupby('year')['rating'].mean().reset_index()
# print(mean_rating_year[mean_rating_year['year'].isin([2022, 2023, 2024, 2025, 2026])])

#Розрахувати кореляцію між кількістю відгуків та середнім рейтингом товару
product_rating = orders_full.groupby('product').agg(
    count_review=('rating', 'count'),
    mean_rating=('rating', 'mean')
).reset_index()
corr_product_rating = product_rating[['count_review', 'mean_rating']].corr()
# print(corr_product_rating)

# print(rating_by_cat[['category', 'rating']])

orders_full = orders_full.merge(customers[['customer_id', 'segment']], on='customer_id', how='inner')
segment_rating = orders_full.groupby('segment')['rating'].mean().round(2).reset_index()
# print(segment_rating)

#Лінійний графік середнього рейтингу за місяцями
mean_rat_by_month = orders_full.groupby('month')['rating'].mean().round(2).reset_index()
# sns.lineplot(
#     data=mean_rat_by_month,
#     x='month',
#     y='rating',
# )
# plt.xlabel('Months')
# plt.ylabel('Rating')
# plt.title("Average rating by month")
# plt.show()

#Box Plot рейтингу по категоріях
# sns.boxplot(
#     data=orders_full,
#     x='category',
#     y='rating',
#     palette='Set2',
# )
# plt.xlabel('Category')
# plt.ylabel('Rating')
# plt.title('Category Rating')
# plt.xticks(rotation=45)
# plt.show()

#Scatter Plot (кількість відгуків vs середній рейтинг)
# sns.scatterplot(
#     x=[orders_full['rating'].count()],
#     y=[orders_full['rating'].mean()]
# )
# plt.show()
# print(orders_full['rating'].count(), orders_full['rating'].mean())
-----------------------------------------------------------------------------------------------------

# КРИТ Фінансовий відділ виявив, що деякі замовлення зі статусом `completed` **не мають відповідного запису в payments**
payment_orders = payments.merge(orders, on='order_id', how='left')
payment_orders = payment_orders[payment_orders['status'] == 'completed']
payment_orders['method'] = payment_orders['method'].fillna('Unknown')
print(payment_orders['method'].unique())
#Пропусков в столбце 'method' необнаружено. Анализ не требуется.
----------------------------------------------------------------------------------
#Маркетинг хоче запустити акцію до дня народження — знижка 10% у місяць народження. 

# 1. Cкільки клієнтів народилося кожного місяця
customers['birth_date'] = pd.to_datetime(customers['birth_date'])
customers['birth_month'] = customers['birth_date'].dt.month
customers['birth_year'] = customers['birth_date'].dt.year

birth_month = customers.groupby('birth_month')['customer_id'].count().reset_index()

#  2. Визначити середній вік клієнтів (на поточну дату) — чи всі > 18?
current_year = pd.to_datetime('now').year
customers['age'] = (current_year - customers['birth_year'])
mean_age = customers['age'].mean()

print(f"Средний возраст клиентов: {mean_age:.2f} лет")
print(f"Количество клиентов младше 18 лет: {(customers['age'] < 18).sum()}")

# 3. Чи є сезонність: клієнти, народжені влітку, купують більше?
customers['season_birth'] = np.where(
    customers['birth_month'].isin([12, 1, 2]), 'winter',
    np.where(customers['birth_month'].isin([3, 4, 5]), 'spring',
    np.where(customers['birth_month'].isin([6, 7, 8]), 'summer',
    'autumn'))
)
order_items['revenue'] = (order_items['quantity'] * order_items['unit_price'] *  (1 - order_items['discount'])).round(2)
orders_revenue = orders[['customer_id', 'order_id']].merge(order_items[['order_id', 'revenue']], on='order_id', how='inner')
customers_revenue = customers.merge(orders_revenue, on='customer_id', how='inner')
season_birth_orders = customers_revenue.groupby('season_birth').agg(
    total_revenue=('revenue', 'sum'),
    total_orders=('order_id', 'count')
).reset_index().sort_values(by=['total_revenue', 'total_orders'], ascending=False)
season_birth_orders
print('Да, клиенты с ДР летом, покупают чаще и на большую выручку для кампании.')

# 4. Порахувати потенційний revenue від акції:
# скільки клієнтів мають день народження в поточному місяці, помножити на середній чек
current_month = pd.to_datetime('now').month
potention_revenue = ((customers['birth_month'] == current_month).count() * customers_revenue['revenue'].mean()).round(2)
print(f'Потенциальный revenue: {potention_revenue}')

# 5. Побудувати pie chart — частка клієнтів за місяцями народження
plt.figure(figsize=(8, 8))
plt.pie(
    x=birth_month['customer_id'],
    labels=birth_month['birth_month'],
    autopct='%1.1f%%'
)
plt.title('Распределение клиентов по месяцам рождения')
plt.show()
#------------------------------------------------------------------------------------------------------------------------------

#2.2 Скоринг ризику відтоку (Churn Risk Scoring) 
total_orders_per_customer = orders.groupby('customer_id')['order_id'].count().reset_index().rename(columns={'order_id': 'total_orders'})
returned_orders_per_customer = orders[orders['status'] == 'returned'].groupby('customer_id')['order_id'].count().reset_index().rename(columns={'order_id': 'returned_orders'})

customer_return_rate = pd.merge(total_orders_per_customer, returned_orders_per_customer, on='customer_id', how='left')
customer_return_rate['returned_orders'] = customer_return_rate['returned_orders'].fillna(0)
customer_return_rate['return_rate'] = (customer_return_rate['returned_orders'] / customer_return_rate['total_orders']).fillna(0)

customer_avg_rating = reviews.groupby('customer_id')['rating'].mean().reset_index()
customer_avg_rating = customer_avg_rating.rename(columns={'rating': 'avg_rating'})

orders['order_date'] = pd.to_datetime(orders['order_date'])

def calculate_frequency_decline(customer_orders):
    if len(customer_orders) < 2:
        return 0
    customer_orders = customer_orders.sort_values(by='order_date')
    time_diffs = customer_orders['order_date'].diff().dropna()
    return time_diffs.mean().total_seconds() / (24 * 3600)

customer_frequency_decline = orders.groupby('customer_id').apply(calculate_frequency_decline).reset_index(name='frequency_decline')

latest_order_date = orders.groupby('customer_id')['order_date'].max().reset_index()
cutoff_date = orders['order_date'].max()

days_since_last_order_df = latest_order_date.copy()
days_since_last_order_df['days_since_last_order'] = (cutoff_date - days_since_last_order_df['order_date']).dt.days
days_since_last_order_df = days_since_last_order_df[['customer_id', 'days_since_last_order']]

churn_features_df = days_since_last_order_df.merge(customer_return_rate[['customer_id', 'return_rate']], on='customer_id', how='left')
churn_features_df = churn_features_df.merge(customer_avg_rating, on='customer_id', how='left')
churn_features_df = churn_features_df.merge(customer_frequency_decline, on='customer_id', how='left')

churn_features_df['avg_rating'] = churn_features_df['avg_rating'].fillna(churn_features_df['avg_rating'].mean())
churn_features_df['frequency_decline'] = churn_features_df['frequency_decline'].fillna(0)

churn_features_df = days_since_last_order_df.merge(customer_return_rate[['customer_id', 'return_rate']], on='customer_id', how='left')
churn_features_df = churn_features_df.merge(customer_avg_rating, on='customer_id', how='left')
churn_features_df = churn_features_df.merge(customer_frequency_decline, on='customer_id', how='left')

churn_features_df['avg_rating'] = churn_features_df['avg_rating'].fillna(churn_features_df['avg_rating'].mean())
churn_features_df['frequency_decline'] = churn_features_df['frequency_decline'].fillna(0)

churn_features_df['churn_risk_group'] = 'Low Risk'
churn_features_df.loc[churn_features_df['days_since_last_order'] > 90, 'churn_risk_group'] = 'Medium Risk'
churn_features_df.loc[churn_features_df['days_since_last_order'] > 180, 'churn_risk_group'] = 'High Risk'

print("Churn Risk Group Distribution:")
print(churn_features_df['churn_risk_group'].value_counts())

churn_analysis_df = churn_features_df.merge(customers[['customer_id', 'segment']], on='customer_id', how='left')

print("\nChurn Risk by Segment:")
churn_analysis_df.groupby('segment')['churn_risk_group'].value_counts(normalize=True).unstack().fillna(0)
churn_by_segment_pivot = churn_analysis_df.groupby('segment')['churn_risk_group'].value_counts(normalize=True).unstack().fillna(0)

for col in ['Low Risk', 'Medium Risk', 'High Risk']:
    if col not in churn_by_segment_pivot.columns:
        churn_by_segment_pivot[col] = 0
churn_by_segment_pivot = churn_by_segment_pivot[['Low Risk', 'Medium Risk', 'High Risk']]

fig, ax = plt.subplots(figsize=(10, 6))
churn_by_segment_pivot.plot(kind='bar', stacked=True, ax=ax, cmap='viridis')

ax.set_title('Распределение риска оттока по сегментам клиентов')
ax.set_xlabel('Сегмент клиентов')
ax.set_ylabel('Доля клиентов')
ax.tick_params(axis='x', rotation=45)
ax.legend(title='Группа риска оттока', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
#---------------------------------------------------------
