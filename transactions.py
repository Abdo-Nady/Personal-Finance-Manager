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

def edit_or_delete_transaction(user, profile):
    print('\n--- All Your Transactions ---')
    if not os.path.exists(TRANSACTIONS_FILE):
        print('No transactions found!')
        return
    
    all_transactions = []
    profile_transactions = []
        
    with open(TRANSACTIONS_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {key.strip(): value for key, value in row.items()}
            all_transactions.append(cleaned_row)
            if cleaned_row.get('profile_id') == profile['profile_id']:
                profile_transactions.append(cleaned_row)
                display_transaction(cleaned_row, profile)
    
    if not profile_transactions:
        print('You have no transactions in this profile!')
        return
    
    txn_id = input('\nEnter the Transaction ID to edit or delete: ').strip()
    if not txn_id:
        print('Transaction ID cannot be empty!')
        return
    
    target_txn = None
    for txn in all_transactions:
        if txn['transaction_id'] == txn_id and txn.get('profile_id') == profile['profile_id']:
            target_txn = txn
            break
    
 
    if not target_txn:
        print('Transaction not found in this profile!')
        return
    
    action = input('Enter "e" to edit or "d" to delete: ').lower()
    
    if action == 'e':
        print('\n--- Edit Transaction (press Enter to keep current value) ---')
        
        new_amount = input(f'Amount (current: {target_txn["amount"]}): ')
        if new_amount:
            try:
                validated_amount = Decimal(new_amount)
                if validated_amount <= 0:
                    print('Amount must be greater than 0! Keeping current value.')
                else:
                    target_txn['amount'] = str(validated_amount)
            except:
                print('Invalid amount! Keeping current value.')
        
        target_txn['category'] = input(f'Category (current: {target_txn["category"]}): ') or target_txn['category']
        
        new_date = input(f'Date (current: {target_txn["date"]}): ')
        if new_date:
            try:
                datetime.datetime.strptime(new_date, '%Y-%m-%d')
                target_txn['date'] = new_date
            except ValueError:
                print('Invalid date format! Keeping current value.')
        
        target_txn['description'] = input(f'Description (current: {target_txn["description"]}): ') or target_txn['description']
        target_txn['payment_method'] = input(f'Payment method (current: {target_txn["payment_method"]}): ') or target_txn['payment_method']
        print('Transaction updated successfully!')
        
    elif action == 'd':
        password = getpass.getpass('Enter your password to confirm deletion:  ')
        users = load_users()
        for u in users:
            if u["name"] == user and verify_password(password, u["password"]):
                break
        else:
            print('Authentication failed! Transaction not deleted.')
            return
        all_transactions.remove(target_txn)
        print('Transaction deleted successfully!')
        
    else:
        print('Invalid action!')
        return
    
    with open(TRANSACTIONS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for txn in all_transactions:
            writer.writerow(txn)


