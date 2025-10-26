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





