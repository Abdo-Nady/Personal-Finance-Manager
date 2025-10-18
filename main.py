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
    

    
    
def HomePage():
    print('Welcome to your Expense Tracker Home Page!')
    print( f'Hello,{user}!')
    print('1. Transactions ')
    print('2. Reports')
    print('3. Switch User')
    print('4. Logout ')
    choice = input('Please select an option: ')
    


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


