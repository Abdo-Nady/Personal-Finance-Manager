import csv
import os
import datetime
from decimal import Decimal
from collections import defaultdict

TRANSACTIONS_FILE = "data/transaction.csv"

def Reports(user, profile):
    """
    Reports dashboard for a given user and profile.
    Shows summary of income, expenses, net savings, and top categories.
    """
    if not os.path.exists(TRANSACTIONS_FILE):
        print("\n⚠️ No transactions file found. Please add some transactions first.")
        return
    
    print('\n' + '='*60)
    print(f'📊 Reports Dashboard - Profile: {profile["profile_name"]}')
    print('='*60)
    print("1. View Summary Report")
    print("2. View Monthly Report")
    print("3. Back to Home Page")
    
    choice = input("Select an option: ")
    if choice == '1':
        show_summary_report(profile)
    elif choice == '2':
        show_monthly_report(profile)
    elif choice == '3':
        return
    else:
        print("Invalid option. Please try again.")


def show_summary_report(profile):
    """Show overall summary report for the selected profile"""
    transactions = load_profile_transactions(profile["profile_id"])
    if not transactions:
        print("\nNo transactions found for this profile.")
        return

    total_income = Decimal("0")
    total_expense = Decimal("0")
    category_expense = defaultdict(Decimal)

    for txn in transactions:
        amount = Decimal(txn["amount"])
        if txn["type"] == "income":
            total_income += amount
        elif txn["type"] == "expense":
            total_expense += amount
            category_expense[txn["category"]] += amount

    net_savings = total_income - total_expense
    print('\n' + '='*60)
    print(f'💰 Summary Report - {profile["profile_name"]}')
    print('='*60)
    print(f"Total Income : {total_income} {profile['currency']}")
    print(f"Total Expense: {total_expense} {profile['currency']}")
    print(f"Net Savings  : {net_savings} {profile['currency']}")
    
    if category_expense:
        top_category = max(category_expense, key=category_expense.get)
        print(f"\n🔥 Top Spending Category: {top_category} ({category_expense[top_category]} {profile['currency']})")
    
        print("\n📂 Expense Breakdown by Category:")
        print('-'*60)

        # Draw ASCII bar chart
        for cat, amt in sorted(category_expense.items(), key=lambda x: x[1], reverse=True):
            percent = (amt / total_expense * 100).quantize(Decimal("0.01")) if total_expense > 0 else Decimal("0")
            bar_length = int(percent / 3)  # scale factor (100% = ~33 bars)
            bar = '█' * bar_length
            print(f"{cat:<15} | {amt:>10} {profile['currency']} | {percent:>6}% | {bar}")

        print('-'*60)
    else:
        print("\nNo expense categories found.")
    print()


def show_monthly_report(profile):
    """Show monthly report filtered by month and year"""
    transactions = load_profile_transactions(profile["profile_id"])
    if not transactions:
        print("\nNo transactions found for this profile.")
        return

    month_input = input("Enter month (MM) [leave blank for current]: ").strip()
    year_input = input("Enter year (YYYY) [leave blank for current]: ").strip()

    today = datetime.date.today()
    month = int(month_input) if month_input else today.month
    year = int(year_input) if year_input else today.year

    filtered = [
        txn for txn in transactions
        if datetime.datetime.strptime(txn["date"], "%Y-%m-%d").month == month and
           datetime.datetime.strptime(txn["date"], "%Y-%m-%d").year == year
    ]

    if not filtered:
        print(f"\nNo transactions found for {month:02d}-{year}.")
        return

    total_income = sum(Decimal(txn["amount"]) for txn in filtered if txn["type"] == "income")
    total_expense = sum(Decimal(txn["amount"]) for txn in filtered if txn["type"] == "expense")
    net_savings = total_income - total_expense

    print('\n' + '='*60)
    print(f'📆 Monthly Report - {month:02d}/{year}')
    print('='*60)
    print(f"Total Income : {total_income} {profile['currency']}")
    print(f"Total Expense: {total_expense} {profile['currency']}")
    print(f"Net Savings  : {net_savings} {profile['currency']}")
    print('-'*60)

    print("\n🧾 Transactions:")
    print('-'*60)
    for txn in filtered:
        print(f"{txn['date']} | {txn['type'].capitalize():<7} | {txn['category']:<15} | {txn['amount']:>8} {profile['currency']} | {txn['description']}")
    print('-'*60)


