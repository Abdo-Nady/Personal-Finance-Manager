import datetime 
import csv 
import json
import os
import uuid
import bcrypt
from decimal import Decimal


USERS_FILE = "users.json"

# # Transaction Structure
# transaction = {
#                     "transaction_id": "TXN001",
#                     "user_id": "UUID",
#                     "type": "expense",  # or "income"
#                     "amount": 50.00,
#                     "category": "Food",
#                     "date": "2025-10-12",
#                     "description": "Lunch at restaurant",
#                     "payment_method": "Credit Card"
                
# }

# # User Structure 
# user = {
#                                 "user_id": "UUID",
#                                 "name": "John Doe",
#                                 "password": "hashed_password",
#                                 "currency": "USD"
                            
# }


def menu():
    print('Welcome to the Expense Tracker!')
    print('1. Login')
    print('2. Register')
    print('3. Exit')
    choice = input('Please select an option: ')
    return choice

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as f: #
        return json.load(f)
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash it
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register():
    users = load_users()
    username = input('Enter a username: ')
    if any(u["name"] == username for u in users):
        print('Username already exists!')
        return None
    password = input('Enter a password: ')
    
    user_id = str(uuid.uuid4())  

    user = {
        "user_id": user_id,
        "name": username,
        "password": hash_password(password),
        "currency": "USD"
    }
    users.append(user)

    save_users(users)
    print('Registration successful!')
    return username

 


def login():
    users = load_users()
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    for u in users:
       if u["name"] == username and verify_password(password, u["password"]):
           print('Login successful!')
           return username
    print('Invalid username or password!')
    return None
    

    

    
    
def HomePage(user):
    while True:
        print('\n' + '='*50)
        print('Welcome to your Expense Tracker Home Page!')
        print(f'Hello, {user}!')
        print('='*50)
        print('1. Transactions')
        print('2. Reports')
        print('3. Switch User')
        print('4. Logout')
        print('='*50)
        choice = input('Please select an option: ')
        
        if choice == '1':
            Transactions(user)
        elif choice == '2':
            Reports(user)
        elif choice == '3':
            print('Switching user...')
            break  # Exit loop to switch user
        elif choice == '4':
            print('Logging out...')
            break  # Exit loop to logout
        else:
            print('Invalid choice. Please try again.')

def Transactions(user):
    while True:
        print('Transactions Page')
        print('1. Add Expense') 
        print('2. Add Income')
        print('3. view All Transactions')
        print('4. Search / Filter Transactions')
        print('5. Edit or Delete Transaction')
        print('6. Back to Home Page')
        choice = input('Please select an option: ')
        if choice == '1':
            add_transaction(user, 'expense')
            print('Expense added successfully!')

        elif choice == '2':
            add_transaction(user, 'income')
            print('Income added successfully!')
  
        elif choice == '3':
            print('\n--- All Transactions ---')
            if not os.path.exists('transaction.csv'):
                print('No transactions found!')
            else:
                with open('transaction.csv', 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    found = False
                    for row in reader:
                        if row['user_id'] == user:
                            print(row)
                            found = True
                    if not found:
                        print('You have no transactions!')
        elif choice == '4':
            print('Search / Filter Transactions Page')
            # Placeholder for search/filter functionality
        elif choice == '5':
            edit_or_delete_transaction(user)

        elif choice == '6':
            print('Returning to Home Page...')
            break
  
        else:
            print('Invalid choice. Please try again.')
  


def edit_or_delete_transaction(user):
    print('\n--- All Your Transactions ---')
    
    # Load ALL transactions
    all_transactions = []
    user_transactions = []
    
    if not os.path.exists('transaction.csv'):
        print('No transactions found!')
        return
    
    with open('transaction.csv', 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {key.strip(): value for key, value in row.items()}
            all_transactions.append(cleaned_row)
            if cleaned_row['user_id'] == user:
                user_transactions.append(cleaned_row)
                print(cleaned_row)
    
    if not user_transactions:
        print('You have no transactions!')
        return
    
    txn_id = input('\nEnter the Transaction ID to edit or delete: ')

    
    transaction_found = False
    for txn in all_transactions:
        if txn['transaction_id'] == txn_id and txn['user_id'] == user:
            transaction_found = True
            action = input('Enter "e" to edit or "d" to delete: ').lower()
            
            if action == 'e':
                print('\n--- Edit Transaction (press Enter to keep current value) ---')
                
                # Validate amount if user enters new value
                new_amount = input(f'Amount (current: {txn["amount"]}): ')
                if new_amount:
                    try:
                        validated_amount = Decimal(new_amount)
                        if validated_amount <= 0:
                            print(' Amount must be greater than 0! Keeping current value.')
                        else:
                            txn['amount'] = str(validated_amount)
                    except:
                        print(' Invalid amount! Keeping current value.')
                
                txn['category'] = input(f'Category (current: {txn["category"]}): ') or txn['category']
                
                # Validate date if user enters new value
                new_date = input(f'Date (current: {txn["date"]}): ')
                if new_date:
                    try:
                        datetime.datetime.strptime(new_date, '%Y-%m-%d')
                        txn['date'] = new_date
                    except ValueError:
                        print(' Invalid date format! Keeping current value.')
                
                txn['description'] = input(f'Description (current: {txn["description"]}): ') or txn['description']
                txn['payment_method'] = input(f'Payment method (current: {txn["payment_method"]}): ') or txn['payment_method']
                print(' Transaction updated successfully!')
            elif action == 'd':
                all_transactions.remove(txn)
                print(' Transaction deleted successfully!')
            else:
                print(' Invalid action!')
                return
            break
    
    if not transaction_found:
        print(' Transaction not found or does not belong to you!')
        return
    
    # Write back ALL transactions
    with open('transaction.csv', 'w', newline='') as csvfile:
        fieldnames = ['transaction_id', 'user_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for txn in all_transactions:
            writer.writerow(txn)

def add_transaction(user, type_):
    transaction_id = f'TXN{int(datetime.datetime.now().timestamp())}'
    amount_input = input('Enter amount: ')
    try:
        amount = Decimal(amount_input)
        if amount <= 0:
            print(' Amount must be greater than 0!')
            return
    except:
        print(' Invalid amount. Please enter a numeric value.')
        return
    
    category = input('Enter category: ')
    if not category.strip():
        print(' Category cannot be empty!')
        return
    
    date = input('Enter date (YYYY-MM-DD): ')
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print(' Invalid date format. Please use YYYY-MM-DD.')
        return
    
    description = input('Enter description: ')
    payment_method = input('Enter payment method: ')
    
    # Check if file exists BEFORE opening
    file_exists = os.path.exists('transaction.csv')
    
    # Open file ONCE
    with open('transaction.csv', 'a', newline='') as csvfile:
        fieldnames = ['transaction_id', 'user_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header if needed
        if not file_exists or os.stat('transaction.csv').st_size == 0:
            writer.writeheader()
        
        # Write transaction
        writer.writerow({
            'transaction_id': transaction_id,
            'user_id': user,
            'type': type_,
            'amount': str(amount),  # ✅ Convert Decimal to string
            'category': category,
            'date': date,
            'description': description,
            'payment_method': payment_method
        })


def Reports(user):     
    print('Reports Page')
    # Placeholder for reports functionality


if __name__ == '__main__': # Main program loop
    while True:
        choice = menu()
        if choice == '1':
            user = login()
            if user:
                HomePage(user)
        elif choice == '2':
            user = register()
            if user:
                HomePage(user)
        elif choice == '3':
            print('Exiting the program. Goodbye!')
            break
        else:
            print('Invalid choice. Please try again.')


