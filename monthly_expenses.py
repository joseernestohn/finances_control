import sqlite3
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import matplotlib.pyplot as plt

DB_PATH = 'D:\\Python-Projects\\Monthly Expenses\\expenses.db'

def create_table() -> None:
    # Connect to the database (creates the file if it doesn't exist)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                          (id INTEGER PRIMARY KEY, category TEXT, amount REAL, month TEXT)''')

def insert_expense(category: str, amount: float, month: str) -> None:
    # Save category and month with first letter capitalized
    category = category.strip().capitalize()
    month = month.strip().capitalize()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO expenses (category, amount, month) VALUES (?, ?, ?)''',
                       (category, amount, month))

def show_expenses() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        query = '''SELECT category, SUM(amount) AS total FROM expenses GROUP BY category'''
        results = pd.read_sql_query(query, conn)

        if results.empty:
            messagebox.showinfo("Info", "No data to display.")
            return

        fig, axs = plt.subplots(1, 2, figsize=(14, 6))

        # ------- PIE CHART (categories) -------
        # Use one palette for the pie
        pie_colors = plt.cm.Set2.colors  # palette for pie
        # Ensure colors length matches number of categories
        pie_colors = pie_colors[:len(results)]

        # Find index of the largest slice and explode it
        max_idx = int(results['total'].idxmax())
        explode = [0.0] * len(results)
        explode[max_idx] = 0.12  # separate the largest slice

        # Plot pie with shadow and exploded largest slice
        wedges, texts, autotexts = axs[1].pie(
            results['total'],
            labels=None,
            autopct='%1.1f%%',
            startangle=90,
            explode=explode,
            shadow=True,
            colors=pie_colors,
            wedgeprops=dict(edgecolor='w'))
        total_spent = results['total'].sum()
        axs[1].set_title("Spending by Category")
        axs[1].set_xlabel(f"Total Spent: ${total_spent:,.2f}")
        axs[1].legend(results["category"], loc="center left", bbox_to_anchor=(1, 0.5))

        # Improve pie text size
        for t in autotexts:
            t.set_fontsize(9)

        # ------- BAR CHART (months) -------
        query_month = '''SELECT month, SUM(amount) AS total_month FROM expenses GROUP BY month'''
        results_month = pd.read_sql_query(query_month, conn)

        if results_month.empty:
            # If there are categories but no months, still show pie and return
            plt.tight_layout()
            plt.show()
            return

        # Ensure months are in calendar order
        month_order = [
            "January","February","March","April","May","June",
            "July","August","September","October","November","December"]
        results_month["month"] = pd.Categorical(
            results_month["month"].str.capitalize(),
            categories=month_order,
            ordered=True)
        results_month = results_month.sort_values("month").dropna(subset=["month"])

        # Use a different palette for bars (distinct from pie)
        bar_colors = plt.cm.Pastel1.colors  # palette for bars
        bar_colors = bar_colors[:len(results_month)]

        axs[0].bar(results_month["month"], results_month["total_month"], color=bar_colors)
        for i, value in enumerate(results_month["total_month"]):
            axs[0].text(i, value, f"${value:,.2f}", ha='center', va='bottom', fontsize=9)
        axs[0].set_title("Expenses by Month")
        axs[0].set_xlabel("Month")
        axs[0].set_ylabel("Amount")
        axs[0].tick_params(axis='x', rotation=20)

        fig.suptitle("Expenses by Category and by Month", fontsize=16)
        plt.tight_layout()
        plt.show()

def submit_data() -> None:
    category = entry1.get()
    amount = entry2.get()
    month = entry3.get()
    try:
        if category.strip() == "" or month.strip() == "" or amount.strip() == "":
            messagebox.showinfo("Error", "Please fill in all fields.")
            return

        month_cap = month.strip().capitalize()
        if month_cap not in [
            "January","February","March","April","May","June","July",
            "August","September","October","November","December"]:
            messagebox.showinfo("Error", "Invalid month.")
            return
        insert_expense(category, float(amount), month_cap)
        entry1.delete(0, tk.END)
        entry2.delete(0, tk.END)
        entry3.delete(0, tk.END)
    except ValueError:
        messagebox.showinfo("Error", "Amount must be a number.")
    except Exception:
        messagebox.showinfo("Error", "Invalid input.")

# ---- Tkinter UI ----
window = tk.Tk()
window.title("Expenses")
window.geometry("480x280")  # make window bigger

# Fonts
label_font = ("Arial", 12)
entry_font = ("Arial", 12)
button_font = ("Arial", 11, "bold")

# Category
label1 = tk.Label(window, text="Category:", font=label_font)
label1.grid(row=0, column=0, padx=12, pady=10, sticky="e")
entry1 = tk.Entry(window, font=entry_font, width=26)
entry1.grid(row=0, column=1, padx=12, pady=10)

# Amount
label2 = tk.Label(window, text="Amount:", font=label_font)
label2.grid(row=1, column=0, padx=12, pady=10, sticky="e")
entry2 = tk.Entry(window, font=entry_font, width=26)
entry2.grid(row=1, column=1, padx=12, pady=10)

# Month
label3 = tk.Label(window, text="Month:", font=label_font)
label3.grid(row=2, column=0, padx=12, pady=10, sticky="e")
entry3 = tk.Entry(window, font=entry_font, width=26)
entry3.grid(row=2, column=1, padx=12, pady=10)

# Buttons
create_table()
button_submit = tk.Button(window, text="Submit", command=submit_data,
                          font=button_font, bg="#4CAF50", fg="white", width=12)
button_submit.grid(row=3, column=0, padx=12, pady=18)

button_show = tk.Button(window, text="Show Data", command=show_expenses,
                        font=button_font, bg="#2196F3", fg="white", width=12)
button_show.grid(row=3, column=1, padx=12, pady=18)

window.mainloop()
