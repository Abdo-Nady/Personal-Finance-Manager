import datetime 
import csv 
import json
import os
from decimal import Decimal



def menu():
    print('Welcome to the Expense Tracker!')
    print('1. Login')
    print('2. Register')
    print('3. Exit')
    choice = input('Please select an option: ')
    return choice

def load_users():
    if not os.path.exists('users.json'):
        return {}
    with open('users.json', 'r') as f: #
        return json.load(f)
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)
def register():
    users = load_users()
    username = input('Enter a username: ')
    if username in users:
        print('Username already exists!')
        return None
    password = input('Enter a password: ')
    users[username] = {'password': password, 'expenses': []}
    save_users(users)
    print('Registration successful!')
    return username

def login():
    users = load_users()
    username = input('Enter your username: ')
    password = input('Enter your password: ')
    if username in users and users[username]['password'] == password:
        print('Login successful!')
        return username
    else:
        print('Invalid username or password!')
        return None
    

    
    
def expense_tracker(username):
    users = load_users()
    while True:
        print('\nExpense Tracker Menu:')
        print('1. Add Expense')
        print('2. View Expenses')
        print('3. Logout')
        choice = input('Select an option: ')
        if choice == '1':
            print('Adding a new expense:')
        elif choice == '2':
            print('\nYour Expenses:')
           
        elif choice == '3':
            print('Logging out...')
            break
        else:
            print('Invalid choice. Please try again.')



if __name__ == '__main__': # Main program loop
    while True:
        choice = menu()
        if choice == '1':
            user = login()
            if user:
                expense_tracker(user)
        elif choice == '2':
            user = register()
            if user:
                expense_tracker(user)
        elif choice == '3':
            print('Exiting the program. Goodbye!')
            break
        else:
            print('Invalid choice. Please try again.')


