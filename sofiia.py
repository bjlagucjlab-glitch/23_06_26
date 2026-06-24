#2.3 Customer data quality audit
import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DB_PATH = r"C:\Users\Sonyi\Downloads\online_store.db"

# Перевірка, чи існує файл БД за вказаним шляхом
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"Error! Database file not found at the specified path:\n{DB_PATH}"
    )

# Підключення до бази даних
conn = sqlite3.connect(DB_PATH)

# SQL запит для вибірки потрібних колонок про клієнтів та завантаження їх у DF
query = "SELECT customer_id, email, birth_date, gender, country FROM customers"
df = pd.read_sql_query(query, conn)
conn.close()

# Заміна порожніх рядків та пробілів на повноцінні значення NaN для коректного аналізу пропусків
for col in ["email", "birth_date", "gender", "country"]:
    df[col] = df[col].replace(r"^\s*$", None, regex=True).replace("", None)

print("CUSTOMER DATA QUALITY AUDIT AND CLEANING")

# Фіксація унікальних значень статі та країни до очищення даних
unique_gender_before = df["gender"].dropna().unique()
unique_country_before = df["country"].dropna().unique()

num_unique_gender_before = len(unique_gender_before)
num_unique_country_before = len(unique_country_before)

# Виведення початкового стану даних у консоль
print("Inconsistent values BEFORE cleaning:")
print(f"Unique values of 'gender' ({num_unique_gender_before}): {list(unique_gender_before)}")
print(f"Unique values of 'country' ({num_unique_country_before}): {list(unique_country_before)}")

# Функція для стандартизації текстових значень статі
def clean_gender(val):
    if pd.isna(val):
        return None
    val = str(val).strip().lower()
    if val in ["m", "male", "man", "чоловік", "ч"]:
        return "Male"
    elif val in ["f", "female", "woman", "жінка", "ж"]:
        return "Female"
    elif val in ["o", "other", "інше"]:
        return "Other"
    return val.capitalize()

# Функція для стандартизації назв країн
def clean_country(val):
    if pd.isna(val):
        return None
    val = str(val).strip()

    mapping = {
        "usa": "USA", "united states": "USA", "u.s.a.": "USA", "us": "USA",
        "uk": "United Kingdom", "united kingdom": "United Kingdom", "u.k.": "United Kingdom",
        "ua": "Ukraine", "ukraine": "Ukraine", "україна": "Ukraine",
        "germany": "Germany", "de": "Germany", "deutschland": "Germany"
    }

    if val.lower() in mapping:
        return mapping[val.lower()]
    return val.capitalize()


# Застосування функцій очищення та створення нових колонок
df["gender_clean"] = df["gender"].apply(clean_gender)
df["country_clean"] = df["country"].apply(clean_country)

# Фіксація унікальних значень статі та країни після очищення даних
unique_gender_after = df["gender_clean"].dropna().unique()
unique_country_after = df["country_clean"].dropna().unique()

num_unique_gender_after = len(unique_gender_after)
num_unique_country_after = len(unique_country_after)

# Виведення результатів уніфікації для порівняння "ДО" та "ПІСЛЯ"
print("Results of unification:")
print(
    f"Number of unique 'gender': TO = {num_unique_gender_before}  AFTER = {num_unique_gender_after} ({list(unique_gender_after)})")
print(
    f"Number of unique 'country': TO = {num_unique_country_before} AFTER = {num_unique_country_after} ({list(unique_country_after)})")

print("Percentage of gaps in key fields:")
target_cols = ["email", "birth_date", "gender"]
missing_summary = {}

# Розрахунок та виведення відсотка пропущених значень NaN для ключових колонок
for col in target_cols:
    pct_missing = df[col].isnull().mean() * 100
    missing_summary[col] = pct_missing
    print(f"Field '{col}': {pct_missing:.2f}% passes")

# Налаштування сітки графіків Matplotlib для дашборду
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Customer Data Quality Dashboard", fontsize=16, weight="bold", y=0.98)

labels = ["BEFORE cleaning", "AFTER cleaning"]
sizes_gender = [num_unique_gender_before, num_unique_gender_after]
colors = ["#ff9999", "#66b3ff"]

# Графік 1: Діаграма кількості унікальних значень статі
axes[0, 0].pie(sizes_gender, labels=labels, colors=colors, autopct='%1.0f', startangle=90,
               pctdistance=0.75, textprops={'fontsize': 11, 'weight': 'bold'})
centre_circle = plt.Circle((0, 0), 0.50, fc='white')
axes[0, 0].add_artist(centre_circle)
axes[0, 0].set_title("Unique values: Gender\n(Reducing value chaos)", fontsize=12, pad=10)

sizes_country = [num_unique_country_before, num_unique_country_after]
colors_country = ["#ffcc99", "#99ff99"]

# Графік 2: Діаграма кількості унікальних країн
axes[0, 1].pie(sizes_country, labels=labels, colors=colors_country, autopct='%1.0f', startangle=90,
               pctdistance=0.75, textprops={'fontsize': 11, 'weight': 'bold'})
centre_circle_c = plt.Circle((0, 0), 0.50, fc='white')
axes[0, 1].add_artist(centre_circle_c)
axes[0, 1].set_title("Unique values: Country\n(Geography Standardization)", fontsize=12, pad=10)

# Підготовка булевої матриці пропусків, True якщо значення пропущено
matrix_data = df[["email", "birth_date", "gender", "country"]].isnull()

# Графік 3: Теплокарта пропусків у даних
sns.heatmap(matrix_data, cmap="Blues", cbar=False, ax=axes[1, 0], yticklabels=False)
axes[1, 0].set_title("Missing Values Matrix\n[Shaded areas = missing values]", fontsize=12, pad=10)
axes[1, 0].set_ylabel("Customer Records (Rows)")

cols_bar = list(missing_summary.keys())
pcts_bar = list(missing_summary.values())

# Графік 4: Стовпчикова діаграма відсотка пропусків у розрізі полів
sns.barplot(x=cols_bar, y=pcts_bar, palette="muted", ax=axes[1, 1], hue=cols_bar, legend=False)
axes[1, 1].set_title("Percentage of field misses (%)", fontsize=12, pad=10)
axes[1, 1].set_ylabel("Skips (%)")
axes[1, 1].set_ylim(0, max(pcts_bar) * 1.2 if max(pcts_bar) > 0 else 10)

# Додавання текстових підписів з відсотками над кожним стовпчиком графіку
for p in axes[1, 1].patches:
    axes[1, 1].annotate(f"{p.get_height():.2f}%",
                        (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 5), textcoords='offset points', weight='bold')

# Автоматичне вирівнювання елементів інтерфейсу та відображення дашборду
plt.tight_layout()
plt.show()


#2.7 DATA SECURITY ANALYSIS AND PII AUDITS
import os
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

DB_PATH = r"C:\Users\Sonyi\Downloads\online_store.db"

# Перевірка наявності файлу бази даних перед початком роботи
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"Error! Database file not found at the specified path:\n{DB_PATH}"
    )

conn = sqlite3.connect(DB_PATH)

# SQL запит для об'єднання загальних даних клієнтів із чутливими даними (PII)
query = """
SELECT 
    c.customer_id,
    c.city,
    c.birth_date,
    p.phone,
    p.national_id,
    p.card_last4,
    p.full_address
FROM customers c
LEFT JOIN customer_pii p ON c.customer_id = p.customer_id
"""
df = pd.read_sql_query(query, conn)
conn.close()

# Очищення від порожніх рядків та невидимих пробілів у полях із персональними даними
for col in ["phone", "national_id", "card_last4", "full_address"]:
    df[col] = df[col].replace(r"^\s*$", None, regex=True).replace("", None)


print("DATA SECURITY ANALYSIS AND PII AUDITS")

# Створення копії DF для проведення маскування даних
df_anon = df.copy()

# Функція для маскування символів у конфіденційних полях
def mask_value(val):
    if pd.isna(val):
        return "None"
    val_str = str(val).strip()
    if len(val_str) <= 2:
        return "**"
    return "*" * (len(val_str) - 2) + val_str[-2:]

# Застосування маскування до телефону, ідентифікаційного коду та останніх 4 цифр картки
df_anon["phone"] = df_anon["phone"].apply(mask_value)
df_anon["national_id"] = df_anon["national_id"].apply(mask_value)
df_anon["card_last4"] = df_anon["card_last4"].apply(mask_value)

# Виведення перших 5 рядків замаскованого датафрейму для перевірки
print("Masked DataFrame (First 5 rows):")
print(df_anon[["customer_id", "phone", "national_id", "card_last4", "city"]].head().to_string())

# Пошук дублікатів адрес
active_addresses = df[df["full_address"].notnull()]
dup_addresses = active_addresses[active_addresses.duplicated("full_address", keep=False)]
num_dup_address_accounts = dup_addresses["customer_id"].nunique()

# Пошук дублікатів телефонів
active_phones = df[df["phone"].notnull()]
dup_phones = active_phones[active_phones.duplicated("phone", keep=False)]
num_dup_phones = dup_phones["customer_id"].nunique()

# Функція для перевірки правильності формату телефону
def check_plus_prefix(val):
    if pd.isna(val):
        return None
    return str(val).strip().startswith("+")

# Застосування перевірки формату та підрахунок некоректних номерів
df["is_phone_valid_format"] = df["phone"].apply(check_plus_prefix)
invalid_phone_format_count = (df["is_phone_valid_format"] == False).sum()

# Розрахунок віку користувачів на основі поточної дати
current_year = datetime.now().year
df["birth_date"] = pd.to_datetime(df["birth_date"], errors="coerce")
df["age"] = current_year - df["birth_date"].dt.year

# Підрахунок неповнолітніх користувачів та клієнтів із відсутньою датою народження
underage_count = (df["age"] < 18).sum()
missing_age_count = df["birth_date"].isnull().sum()

# Формування та виведення фінального звіту про якість та безпеку персональних даних (PII)
print("PII QUALITY AND SECURITY REPORT TABLE")
print(f"Customers with the same addresses (potential duplicates): {num_dup_address_accounts} persons")
print(f"Customers sharing one phone number with two: {num_dup_phones} persons")
print(f"Phone numbers without the '+' prefix in the database: {invalid_phone_format_count} piece")
print(f"Clients who have NOT passed 18+ verification (minors): {underage_count} persons")
print(f"Clients with missing/incorrect date of birth: {missing_age_count} persons")

# Підрахунок кількості клієнтів у розрізі міст
city_counts = df["city"].value_counts().reset_index()
city_counts.columns = ["City", "Customer Count"]

# Виділення ТОП-15 міст за кількістю користувачів для візуалізації
top_cities = city_counts.head(15)

# Налаштування стилю та розміру графіка
sns.set_theme(style="whitegrid")
plt.figure(figsize=(12, 6))

# Побудова горизонтальної стовпчикової діаграми розподілу клієнтів по містах
ax = sns.barplot(
    x="Customer Count",
    y="City",
    data=top_cities,
    palette="viridis",
    hue="City",
    legend=False
)

# Додавання точних числових значень (кількості клієнтів) праворуч від кожного стовпчика
for p in ax.patches:
    width = p.get_width()
    ax.annotate(
        f"{int(width)}",
        (width, p.get_y() + p.get_height() / 2.0),
        ha="left",
        va="center",
        xytext=(5, 0),
        textcoords="offset points",
        fontsize=10,
        weight="bold"
    )

# Налаштування заголовка та підписів осей графіка
plt.title("Distribution of customer geography: Top cities by number of users", fontsize=14, pad=15)
plt.xlabel("Number of clients (persons)", fontsize=12)
plt.ylabel("City", fontsize=12)

# Оптимізація та виведення графіка на екран
plt.tight_layout()
plt.show()


#2.4 First Purchase Behavior
import os
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DB_PATH = r"C:\Users\Sonyi\Downloads\online_store.db"

# Перевірка, чи існує файл
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"Error! Database file not found at the specified path:\n{DB_PATH}\n"
        f"Please check the correctness of the path."
    )

conn = sqlite3.connect(DB_PATH)

# Складний SQL запит для об'єднання 6 таблиць
# Розраховується чистий дохід за позицію (з урахуванням знижки) та визначається факт повернення товару
query = """
SELECT 
    c.customer_id,
    c.segment,
    c.signup_date,
    o.order_id,
    o.order_date,
    oi.unit_price * oi.quantity * (1 - oi.discount) as item_revenue,
    oi.discount,
    p.category_id,
    cat.name as category_name,
    CASE WHEN r.return_id IS NOT NULL THEN 1 ELSE 0 END as is_returned
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
JOIN categories cat ON p.category_id = cat.category_id
LEFT JOIN returns r ON o.order_id = r.order_id
"""
df_raw = pd.read_sql_query(query, conn)
conn.close()

# Приведення колонок із датами реєстрації та замовлень до правильного формату
df_raw["signup_date"] = pd.to_datetime(df_raw["signup_date"])
df_raw["order_date"] = pd.to_datetime(df_raw["order_date"])

# Розрахунок загальноЇ суми всього доходу від кожного клієнта за весь час
clv_df = (
    df_raw.groupby("customer_id")["item_revenue"].sum().reset_index(name="clv")
)

# Визначення дати найпершого замовлення для кожного клієнта за допомогою віконної функції
df_raw["first_order_date"] = df_raw.groupby("customer_id")[
    "order_date"
].transform("min")

# Фільтрація: залишаються лише записи, що стосуються саме першого замовлення клієнта
df_first_orders_all = df_raw[df_raw["order_date"] == df_raw["first_order_date"]]

# Визначення головної категорії у першому замовленні (якщо товарів кілька, береться той де більший чек)
df_first_category = (
    df_first_orders_all.groupby(["customer_id", "category_name"])[
        "item_revenue"
    ]
    .sum()
    .reset_index()
)
df_first_category = df_first_category.sort_values(
    "item_revenue", ascending=False
).drop_duplicates(subset=["customer_id"])

# Перевірка чи була застосована знижка під час першої покупки клієнта
df_first_discount = (
    df_first_orders_all.groupby("customer_id")["discount"]
    .max()
    .reset_index()
)
df_first_discount["has_discount"] = df_first_discount["discount"] > 0

# Визначення чи було повернення принаймні одного товару з першого замовлення клієнта
df_first_return = (
    df_first_orders_all.groupby("customer_id")["is_returned"].max().reset_index()
)

# Створення фінального агрегованого датафрейму першої покупки клієнта
df_first = df_first_orders_all[
    ["customer_id", "segment", "signup_date", "first_order_date"]
].drop_duplicates()

# Послідовне об'єднання всіх підрахованих раніше даних першої покупки в один датафрейм за customer_id
df_first = df_first.merge(
    df_first_category[["customer_id", "category_name"]], on="customer_id"
)
df_first = df_first.merge(
    df_first_discount[["customer_id", "has_discount"]], on="customer_id"
)
df_first = df_first.merge(df_first_return, on="customer_id")
df_first = df_first.merge(clv_df, on="customer_id")

# Обчислення швидкості першої покупки: кількість днів від моменту реєстрації до першого замовлення
df_first["time_to_first_order"] = (
    df_first["first_order_date"] - df_first["signup_date"]
).dt.days


# Блок аналітики та виведення результатів

print("FIRST PURCHASE BEHAVIOR ANALYSIS")

# Аналіз впливу першої обраної категорії товару на майбутній загальний CLV клієнта
print("\n The impact of the first category on CLV:")
print(
    df_first.groupby("category_name")["clv"]
    .agg(["count", "mean", "median"])
    .to_string()
)

# Аналіз залежності між наявністю знижки на першу покупку та подальшими поверненнями товару
print(" Dependence of returns on the availability of a discount on the first order (%):")
print(
    pd.crosstab(
        df_first["has_discount"], df_first["is_returned"], normalize="index"
    )
    * 100
)

# Загальний статистичний опис часу очікування першої покупки
print(" General description of Time-to-First-Order (in days):")
print(df_first["time_to_first_order"].describe())

# Порівняння швидкості здійснення першої покупки між різними сегментами клієнтів
print(" Time-to-First-Order comparison between segments:")
print(
    df_first.groupby("segment")["time_to_first_order"].agg(["mean", "median"])
)


# Блок візуалізації даних

sns.set_theme(style="whitegrid")

# Графік 1: Boxplot розподілу кількості днів до першої покупки в розрізі сегментів клієнтів
plt.figure(figsize=(10, 6))
sns.boxplot(
    data=df_first,
    x="segment",
    y="time_to_first_order",
    hue="segment",
    palette="Set2",
    legend=False,
)
plt.title("Time-to-First-Order distribution by customer segments", fontsize=14)
plt.xlabel("Customer segment", fontsize=12)
plt.ylabel("Number of days from registration to purchase", fontsize=12)
plt.tight_layout()

# Графік 2: Накопичувальна стовпчикова діаграма, що показує частку товарних категорій у кожному сегменті
plt.figure(figsize=(12, 7))
pivot_df = pd.crosstab(
    df_first["segment"], df_first["category_name"], normalize="index"
) * 100
pivot_df.plot(kind="bar", stacked=True, cmap="tab20", ax=plt.gca())
plt.title(
    "Distribution of the first category of goods within segments (%)", fontsize=14
)
plt.xlabel("Customer segment", fontsize=12)
plt.ylabel("Share (%)", fontsize=12)
plt.xticks(rotation=0)
plt.legend(title="Product category", bbox_to_anchor=(1.02, 1), loc="upper left")
plt.tight_layout()

# Графік 3: Теплокарта перетину початкових категорій та фінальних сегментів користувачів (матриця потоків)
plt.figure(figsize=(10, 6))
sankey_data = pd.crosstab(df_first["category_name"], df_first["segment"])
sns.heatmap(sankey_data, annot=True, fmt="d", cmap="YlGnBu", cbar=True)
plt.title(
    "Flow Matrix: Relationship of First Category (Input) to Segment (Output)",
    fontsize=14,
)
plt.xlabel("End customer segment", fontsize=12)
plt.ylabel("First selected category", fontsize=12)

# Відображення та оптимізація всіх графіків
plt.tight_layout()
plt.show()
