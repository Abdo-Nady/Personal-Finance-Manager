import os
import csv
import datetime
from decimal import Decimal
import getpass
from utils import verify_password
from storage import load_users
from storage import TRANSACTIONS_FILE
from utils import print_header

def add_transaction(user, profile, type_):
    transaction_id = f'TXN{int(datetime.datetime.now().timestamp())}'
    amount_input = input('Enter amount: ')
    try:
        amount = Decimal(amount_input)
        if amount <= 0:
            print('Amount must be greater than 0!')
            return False
    except:
        print('Invalid amount. Please enter a numeric value.')
        return False
    
    category = input('Enter category: ')
    if not category.strip():
        print('Category cannot be empty!')
        return False
    
    date = input('Enter date (YYYY-MM-DD): ')
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print('Invalid date format. Please use YYYY-MM-DD.')
        return False
    
    description = input('Enter description: ')
    
    payment_method = input('Enter payment method: ')
    if not payment_method.strip():
        print('Payment method cannot be empty!')
        return False
    
    file_exists = os.path.exists(TRANSACTIONS_FILE)
    
    try:
        with open(TRANSACTIONS_FILE, 'a', newline='') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists or os.stat(TRANSACTIONS_FILE).st_size == 0:
                writer.writeheader()
            
            writer.writerow({
                'transaction_id': transaction_id,
                'user': user,
                'profile_id': profile['profile_id'],
                'type': type_,
                'amount': str(amount),
                'category': category,
                'date': date,
                'description': description,
                'payment_method': payment_method
            })
        return True
    except Exception as e:
        print(f'Error writing to file: {e}')
        return False

