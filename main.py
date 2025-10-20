import datetime 
import csv 
import json
import os
import uuid
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
        "password": password,
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
       if u["name"] == username and u["password"] == password:
           print('Login successful!')
           return username
       else:
            print('Invalid username or password!')
            return None
    

    

    
    
def HomePage(user):
    print('Welcome to your Expense Tracker Home Page!')
    print( f'Hello,{user}!')
    print('1. Transactions ')
    print('2. Reports')
    print('3. Switch User')
    print('4. Logout ')
    choice = input('Please select an option: ')
    if choice == '1':
        Transactions(user)
    elif choice == '2':
        Reports(user)
    elif choice == '3':
        print('Switching user...')
        return
    elif choice == '4':
        print('Logging out...')
        return
    else:
        print('Invalid choice. Please try again.')
        HomePage(user)

def Transactions(user):
    users = load_users()
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
        Transactions(user)
    elif choice == '2':
        add_transaction(user, 'income')
        print('Income added successfully!')
        Transactions(user)
    elif choice == '3':
        print('All Transactions:')
        with open('transaction.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user:
                    print(row)
        Transactions(user)
    elif choice == '4':
        print('Search / Filter Transactions Page')
        # Placeholder for search/filter functionality
        Transactions(user)
    elif choice == '5':
        print(' All Transactions:')
        transactions = []
        with open('transaction.csv', 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['user_id'] == user:
                    transactions.append(row)
                    print(row)
        txn_id = input('Enter the Transaction ID to edit or delete: ')
        for txn in transactions:
            if txn['transaction_id'] == txn_id:
                action = input('Enter "e" to edit or "d" to delete: ')
                if action == 'e':
                    txn['amount'] = input(f'Enter new amount (current: {txn["amount"]}): ') or txn['amount']
                    txn['category'] = input(f'Enter new category (current: {txn["category"]}): ') or txn['category']
                    txn['date'] = input(f'Enter new date (current: {txn["date"]}): ') or txn['date']
                    txn['description'] = input(f'Enter new description (current: {txn["description"]}): ') or txn['description']
                    txn['payment_method'] = input(f'Enter new payment method (current: {txn["payment_method"]}): ') or txn['payment_method']
                    print('Transaction updated successfully!')
                elif action == 'd':
                    transactions.remove(txn)
                    print('Transaction deleted successfully!')
                break
        with open('transaction.csv', 'w', newline='') as csvfile:
            fieldnames = ['transaction_id', 'user_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for txn in transactions:
                writer.writerow(txn)
        Transactions(user)
    elif choice == '6':
        HomePage(user)  
    else:
        print('Invalid choice. Please try again.')
        Transactions(user)

def add_transaction(user, type_):
    transaction_id = f'TXN{int(datetime.datetime.now().timestamp())}'
    amount = input('Enter amount: ')
    category = input('Enter category: ')
    date = input('Enter date (YYYY-MM-DD): ')
    description = input('Enter description: ')
    payment_method = input('Enter payment method: ')
    with open('transaction.csv', 'a', newline='') as csvfile:
        fieldnames = ['transaction_id', 'user_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if os.stat('transaction.csv').st_size == 0:
            writer.writeheader()
        writer.writerow({
            'transaction_id': transaction_id,
            'user_id': user,
            'type': type_,
            'amount': amount,
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



