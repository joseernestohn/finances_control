import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------- DATABASE ---------------- #
DB_PATH = "expenses.db"

def create_table():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                          (id INTEGER PRIMARY KEY, category TEXT, amount REAL, month TEXT)''')

def insert_expense(category, amount, month):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO expenses (category, amount, month) VALUES (?, ?, ?)',
                       (category.capitalize(), amount, month.capitalize()))
        conn.commit()

def get_data():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query("SELECT * FROM expenses", conn)

def get_summary():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)

# ---------------- STREAMLIT APP ---------------- #
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="centered")
st.title("💰 Expense Tracker")

create_table()

# --- Expense input form --- #
st.subheader("➕ Add a new expense")

with st.form("expense_form"):
    category = st.text_input("Category")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    month = st.selectbox("Month", [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ])
    submitted = st.form_submit_button("Add")
    if submitted and category and amount > 0:
        insert_expense(category, amount, month)
        st.success(f"Expense added: {category} - ${amount} ({month})")

# --- Show stored data --- #
st.subheader("📊 Stored Data")
if st.checkbox("Show table of expenses"):
    df = get_data()
    if not df.empty:
        st.dataframe(df)
    else:
        st.info("No data yet.")

# --- Summary by category --- #
st.subheader("📈 Summary by Category")
if st.checkbox("Show summary"):
    summary = get_summary()
    if not summary.empty:
        st.bar_chart(summary.set_index("category"))
    else:
        st.info("No data to summarize.")

# --- Matplotlib chart --- #
st.subheader("📉 Expense Distribution")
if st.checkbox("Show pie chart (Matplotlib)"):
    summary = get_summary()
    if not summary.empty:
        fig, ax = plt.subplots()
        ax.pie(summary["total"], labels=summary["category"], autopct="%1.1f%%")
        ax.set_title("Expense distribution by category")
        st.pyplot(fig)
    else:
        st.info("No data to plot.")


