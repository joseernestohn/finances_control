import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ---------------- DATABASE ---------------- #
DB_PATH = "expenses_app.db"  # works in Streamlit Cloud

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

def get_category_summary():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT category, SUM(amount) as total FROM expenses GROUP BY category", conn)

def get_month_summary():
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            "SELECT month, SUM(amount) as total FROM expenses GROUP BY month", conn)

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
        "July","August","September","October","November","December"])
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

# --- Bar chart by month --- #
st.subheader("📈 Summary by Month")
if st.checkbox("Show monthly summary"):
    month_summary = get_month_summary()
    if not month_summary.empty:
        # Order months correctly
        month_order = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"]
        month_summary["month"] = pd.Categorical(
            month_summary["month"].str.capitalize(),
            categories=month_order,
            ordered=True)
        month_summary = month_summary.sort_values("month").dropna(subset=["month"])

        fig, ax = plt.subplots(figsize=(10,5))
        ax.bar(month_summary["month"], month_summary["total"], color=plt.cm.Pastel1.colors[:len(month_summary)])
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        ax.set_title("Expenses by Month")
        ax.tick_params(axis='x', rotation=15)  # slight tilt
        for i, value in enumerate(month_summary["total"]):
            ax.text(i, value, f"${value:,.2f}", ha='center', va='bottom', fontsize=9)
        st.pyplot(fig)
    else:
        st.info("No data to summarize by month.")

# --- Pie chart by category --- #
st.subheader("📉 Expense Distribution")
if st.checkbox("Show pie chart (by category)"):
    category_summary = get_category_summary()
    if not category_summary.empty:
        fig, ax = plt.subplots(figsize=(6,6))
        ax.pie(category_summary["total"], labels=category_summary["category"], autopct="%1.1f%%",
               colors=plt.cm.Pastel2.colors[:len(category_summary)], wedgeprops=dict(edgecolor='w'))
        ax.set_title("Expense distribution by category")
        st.pyplot(fig)
    else:
        st.info("No data to plot.")

# --- Clear all expenses from database --- #
st.subheader("🗑️ Clear All Expenses")
if st.button("Clear Database"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses")  # delete all rows
        conn.commit()
    st.success("All expenses have been deleted!")








