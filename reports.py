import csv
import os
import datetime
from decimal import Decimal
from collections import defaultdict
from financial_health import show_financial_health
from utils import clear_screen

TRANSACTIONS_FILE = "data/transaction.csv"

def Reports(user, profile):
    """
    Reports dashboard for a given user and profile.
    Shows summary of income, expenses, net savings, and top categories.
    """
    if not os.path.exists(TRANSACTIONS_FILE):
        print("\nNo transactions file found. Please add some transactions first.")
        input("\nPress Enter to continue...")
        return
    
    while True:  
        clear_screen()
        print('\n' + '='*60)
        print(f'Reports Dashboard - Profile: {profile["profile_name"]}')
        print('='*60)
        print("1. View Summary Report")
        print("2. View Monthly Report")
        print("3. View Financial Health Score")
        print("4. Back to Home Page")
        print('='*60)
        
        choice = input("Select an option: ").strip()
        
        choice = input("Select an option ✎𓂃  ")
        if choice == '1':
            show_summary_report(profile)
        elif choice == '2':
            show_monthly_report(profile)
        elif choice == '3':
            show_financial_health(profile)
        elif choice == '4':
            break  
        else:
            print("\nInvalid option. Please try again.")
            input("\nPress Enter to continue...")


def show_summary_report(profile):
    """Show overall summary report for the selected profile"""
    clear_screen()
    
    transactions = load_profile_transactions(profile["profile_id"])
    if not transactions:
        print("\nNo transactions found for this profile.")
        input("\nPress Enter to continue...")
        return

    total_income = Decimal("0")
    total_expense = Decimal("0")
    category_expense = defaultdict(Decimal)

    for txn in transactions:
        try:
            amount = Decimal(txn["amount"])
            if txn["type"] == "income":
                total_income += amount
            elif txn["type"] == "expense":
                total_expense += amount
                category_expense[txn["category"]] += amount
        except (ValueError, KeyError):
            # تجاهل المعاملات ذات البيانات التالفة
            continue

    net_savings = total_income - total_expense
    
    print('\n' + '='*60)
    print(f'Summary Report - {profile["profile_name"]}')
    print('='*60)
    print(f"Total Income : {total_income} {profile['currency']}")
    print(f"Total Expense: {total_expense} {profile['currency']}")
    print(f"Net Savings  : {net_savings} {profile['currency']}")
    
    if category_expense:
        top_category = max(category_expense, key=category_expense.get)
        print(f"\nTop Spending Category: {top_category} ({category_expense[top_category]} {profile['currency']})")

        print("\nExpense Breakdown by Category:")
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
    
    input("\nPress Enter to continue...")


def show_monthly_report(profile):
    """Show monthly report filtered by month and year"""
    clear_screen()
    
    transactions = load_profile_transactions(profile["profile_id"])
    if not transactions:
        print("\nNo transactions found for this profile.")
        input("\nPress Enter to continue...")
        return

    month_input = input("Enter month (MM) [leave blank for current]: ").strip()
    year_input = input("Enter year (YYYY) [leave blank for current]: ").strip()

    today = datetime.date.today()
    
    # معالجة الأخطاء عند التحويل
    try:
        month = int(month_input) if month_input else today.month
        year = int(year_input) if year_input else today.year
        
        # التحقق من صحة الشهر
        if not (1 <= month <= 12):
            print("\nInvalid month! Must be between 1 and 12.")
            input("\nPress Enter to continue...")
            return
            
        # التحقق من صحة السنة
        if year < 1900 or year > 2100:
            print("\nInvalid year! Must be between 1900 and 2100.")
            input("\nPress Enter to continue...")
            return
    except ValueError:
        print("\nInvalid input! Please enter numeric values.")
        input("\nPress Enter to continue...")
        return

    filtered = []
    for txn in transactions:
        try:
            txn_date = datetime.datetime.strptime(txn["date"], "%Y-%m-%d")
            if txn_date.month == month and txn_date.year == year:
                filtered.append(txn)
        except (ValueError, KeyError):
            # تجاهل المعاملات ذات التواريخ التالفة
            continue

    if not filtered:
        print(f"\nNo transactions found for {month:02d}/{year}.")
        input("\nPress Enter to continue...")
        return

    total_income = Decimal("0")
    total_expense = Decimal("0")
    
    for txn in filtered:
        try:
            amount = Decimal(txn["amount"])
            if txn["type"] == "income":
                total_income += amount
            elif txn["type"] == "expense":
                total_expense += amount
        except (ValueError, KeyError):
            continue
    
    net_savings = total_income - total_expense

    print('\n' + '='*60)
    print(f'Monthly Report - {month:02d}/{year}')
    print('='*60)
    print(f"Total Income : {total_income} {profile['currency']}")
    print(f"Total Expense: {total_expense} {profile['currency']}")
    print(f"Net Savings  : {net_savings} {profile['currency']}")
    print('-'*60)

    print("\nTransactions:")
    print('-'*60)
    for txn in filtered:
        print(f"{txn['date']} | {txn['type'].capitalize():<7} | {txn['category']:<15} | {txn['amount']:>8} {profile['currency']} | {txn['description']}")
    print('-'*60)
    
    input("\nPress Enter to continue...")


def load_profile_transactions(profile_id):
    """Helper function to load all transactions for a given profile_id"""
    transactions = []
    if not os.path.exists(TRANSACTIONS_FILE):
        return transactions

    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned = {k.strip(): v.strip() for k, v in row.items()}
                if cleaned.get("profile_id") == profile_id:
                    transactions.append(cleaned)
    except Exception as e:
        print(f"\nError loading transactions: {e}")
    
    return transactions