import datetime 
import csv 
import json
import os
import getpass
import uuid
import bcrypt
from decimal import Decimal


USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transaction.csv"

def menu(): # Main menu function
    print('Welcome to the Expense Tracker!')
    print('1. Login')
    print('2. Register')
    print('3. Exit')
    choice = input('Please select an option: ')
    return choice

def load_users(): #a function to load users from the JSON file
    if not os.path.exists(USERS_FILE): 
        return []
    try:
        with open(USERS_FILE, 'r') as f: 
            return json.load(f)
    except json.JSONDecodeError:    
        return []
    
def save_users(users): #a function to save users to the JSON file
   try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
   except Exception as e:
        print(f"Error saving users: {e}")

def hash_password(password): #function to hash passwords
    """Hash a password using bcrypt"""
    # Convert password to bytes and hash it
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8') # Convert back to string for storage

def verify_password(password, hashed_password): #function to verify passwords
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) # Convert back to bytes for verification

def register(): # Function to handle user registration
    users = load_users()
    username = input('Enter a username: ')
    if any(u["name"] == username for u in users):
        print('Username already exists!')
        return None
    password = getpass.getpass('Enter a password:  ')
    currency = input('Enter your preferred currency (default is USD): ')
    if not currency.strip():
        currency = "USD"
    
    user_id = str(uuid.uuid4())  

    user = {
        "user_id": user_id,
        "name": username,
        "password": hash_password(password),
        "currency": currency
    }
    users.append(user)

    save_users(users)
    print('Registration successful!')
    return username

 


def login(): # Function to handle user login
    users = load_users()
    username = input('Enter your username: ')
    password = getpass.getpass('Enter your password:  ')
    for u in users:
       if u["name"] == username and verify_password(password, u["password"]):
           print('Login successful!')
           return username
    print('Invalid username or password!')
    return None
    

    

    
    
def HomePage(user): # Function for the home page
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

def Transactions(user): # Function to handle transactions
    while True:
        print('\n' + '='*50) 
        print('Transactions Page')
        print('='*50)
        print('1. Add Expense') 
        print('2. Add Income')
        print('3. view All Transactions')
        print('4. Search / Filter Transactions')
        print('5. Edit or Delete Transaction')
        print('6. Back to Home Page')
        choice = input('Please select an option: ')
        if choice == '1':
            if add_transaction(user, 'expense'):
                print('Expense added successfully!')
            else:
                print('Failed to add expense.')

        elif choice == '2':
            if add_transaction(user, 'income'):
                print('Income added successfully!')
            else:
                print('Failed to add income.')
        elif choice == '3':
            print('\n--- All Transactions ---')
            if not os.path.exists(TRANSACTIONS_FILE):
                print('No transactions found!')
            else:
                with open(TRANSACTIONS_FILE, 'r') as csvfile:
                    reader = csv.DictReader(csvfile)
                    found = False
                    for row in reader:
                        cleaned_row = {key.strip(): value for key, value in row.items()}  # ✅
                        if cleaned_row['user'] == user:
                            display_transaction(cleaned_row)
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
  


def edit_or_delete_transaction(user): # Function to edit or delete a transaction
    print('\n--- All Your Transactions ---')
    
    # Load ALL transactions
    all_transactions = []
    user_transactions = []
    
    if not os.path.exists(TRANSACTIONS_FILE):
        print('No transactions found!')
        return
    
    with open(TRANSACTIONS_FILE, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {key.strip(): value for key, value in row.items()}
            all_transactions.append(cleaned_row)
            if cleaned_row['user'] == user:
                user_transactions.append(cleaned_row)
                display_transaction(cleaned_row)
    
    if not user_transactions:
        print('You have no transactions!')
        return
    
    txn_id = input('\nEnter the Transaction ID to edit or delete: ')

    
    transaction_found = False
    for txn in all_transactions:
        if txn['transaction_id'] == txn_id and txn['user'] == user:
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
                            print('Amount must be greater than 0! Keeping current value.')
                        else:
                            txn['amount'] = str(validated_amount)
                    except:
                        print('Invalid amount! Keeping current value.')
                
                txn['category'] = input(f'Category (current: {txn["category"]}): ') or txn['category']
                
                # Validate date if user enters new value
                new_date = input(f'Date (current: {txn["date"]}): ')
                if new_date:
                    try:
                        datetime.datetime.strptime(new_date, '%Y-%m-%d')
                        txn['date'] = new_date
                    except ValueError:
                        print('Invalid date format! Keeping current value.')
                
                txn['description'] = input(f'Description (current: {txn["description"]}): ') or txn['description']
                txn['payment_method'] = input(f'Payment method (current: {txn["payment_method"]}): ') or txn['payment_method']
                print('Transaction updated successfully!')
            elif action == 'd':
                #authenticate before deletion
                password = getpass.getpass('Enter your password to confirm deletion:  ')
                users = load_users()
                for u in users:
                    if u["name"] == user and verify_password(password, u["password"]):
                        break
                else:
                    print('Authentication failed! Transaction not deleted.')
                    return
                all_transactions.remove(txn)
                print('Transaction deleted successfully!')
            else:
                print('Invalid action!')
                return
            break
    
    if not transaction_found:
        print('Transaction not found or does not belong to you!')
        return
    
    # Write back ALL transactions
    with open(TRANSACTIONS_FILE, 'w', newline='') as csvfile:
        fieldnames = ['transaction_id', 'user', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for txn in all_transactions:
            writer.writerow(txn)

def add_transaction(user, type_): # Function to add a transaction
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
    
    # Check if file exists BEFORE opening
    file_exists = os.path.exists(TRANSACTIONS_FILE)
    
    # Open file ONCE
    try:
        with open(TRANSACTIONS_FILE, 'a', newline='') as csvfile:
            fieldnames = ['transaction_id', 'user', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header if needed
            if not file_exists or os.stat(TRANSACTIONS_FILE).st_size == 0:
                writer.writeheader()
            
            # Write transaction
            writer.writerow({
                'transaction_id': transaction_id,
                'user': user,
                'type': type_,
                'amount': str(amount),  # ✅ Convert Decimal to string
                'category': category,
                'date': date,
                'description': description,
                'payment_method': payment_method
            })
        return True
    except Exception as e:
        print(f'Error writing to file: {e}')
        return False

def display_transaction(txn): # Function to display a transaction
    """Display a transaction in a readable format"""
    print(f"\nID: {txn['transaction_id']}")
    print(f"Type: {txn['type'].capitalize()}")
    print(f"Amount: {txn['amount']}")
    print(f"Category: {txn['category']}")
    print(f"Date: {txn['date']}")
    print(f"Description: {txn['description']}")
    print(f"Payment: {txn['payment_method']}")
    print('-' * 40)

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


