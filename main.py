import datetime 
import csv 
import json
import os
import getpass
import uuid
import bcrypt
from decimal import Decimal
import shutil # backup files

USERS_FILE = "users.json"
TRANSACTIONS_FILE = "transaction.csv"
BACKUP_DIR = "backups"
LAST_BACKUP_FILE = "last_backup.txt"



def should_backup():
    """Check if we need to backup this month"""
    if not os.path.exists(LAST_BACKUP_FILE):
        return True
    
    try:
        with open(LAST_BACKUP_FILE, 'r') as f:
            last_backup = f.read().strip()
            current_month = datetime.datetime.now().strftime('%Y-%m')
            return last_backup != current_month
    except:
        return True


def monthly_backup():
    """Create backup once per month"""
    if not should_backup():
        return
    
    timestamp = datetime.datetime.now().strftime('%Y-%m')  # YYYY-MM format
    
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    try:
        backup_count = 0
        if os.path.exists(USERS_FILE):
            shutil.copy2(USERS_FILE, f"{BACKUP_DIR}/users_{timestamp}.json")
            backup_count += 1
        
        if os.path.exists(TRANSACTIONS_FILE):
            shutil.copy2(TRANSACTIONS_FILE, f"{BACKUP_DIR}/transaction_{timestamp}.csv")
            backup_count += 1
        
        if backup_count > 0:
            # Update last backup date
            with open(LAST_BACKUP_FILE, 'w') as f:
                f.write(datetime.datetime.now().strftime('%Y-%m'))
            
            print(f"\n{'='*50}")
            print(f"✅ Monthly backup created successfully! ({timestamp})")
            print(f"{'='*50}\n")
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")
        
        
        
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
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f: 
            return json.load(f) 
    except json.JSONDecodeError:        
        return []
    
def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
    except Exception as e:
        print(f"Error saving users: {e}")

def hash_password(password):
    """Hash a password using bcrypt"""
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
    password = getpass.getpass('Enter a password:  ')
    
    user_id = str(uuid.uuid4())
    
    # Create default profile
    profile_name = input('Enter profile name: ')
    if not profile_name.strip():
        print('Profile name cannot be empty!')
        return
    
    currency = input('Enter currency (default is USD): ')
    if not currency.strip():
        currency = "USD"
        
    default_profile = create_profile_data(profile_name, currency)
    
    user = {
        "user_id": user_id,
        "name": username,
        "password": hash_password(password),
        "profiles": [default_profile]
    }
    users.append(user)

    save_users(users)
    print('Registration successful!')
    print(f'Created default profile "{profile_name}" with currency "{currency}".')
    return username

def create_profile_data(profile_name, currency):
    """Helper function to create profile data structure"""
    return {
        "profile_id": str(uuid.uuid4()),
        "profile_name": profile_name,
        "currency": currency
    }

def login():
    users = load_users()
    username = input('Enter your username: ')
    password = getpass.getpass('Enter your password:  ')
    for u in users:
       if u["name"] == username and verify_password(password, u["password"]):
           print('Login successful!')
           return username
    print('Invalid username or password!')
    return None

def get_user_data(username):
    """Get user data by username"""
    users = load_users()
    for u in users:
        if u["name"] == username:
            return u
    return None

def profile_menu(user):
    """Display profile selection/management menu"""
    user_data = get_user_data(user)
    if not user_data:  # defensive programming in case json is corrupted 
        print("Error: User data not found! Please login again.")
        return None
     
    while True:
        print('\n' + '='*50)
        print('Profile Management')
        print('='*50)
        print('Your Profiles:')
        for idx, profile in enumerate(user_data["profiles"], 1):
            print(f'{idx}. {profile["profile_name"]} (Currency: {profile["currency"]})')
        print('='*50)
        print(f'{len(user_data["profiles"]) + 1}. Create New Profile')
        print(f'{len(user_data["profiles"]) + 2}. Delete Profile')
        print(f'{len(user_data["profiles"]) + 3}. Logout')
        print('='*50)
        
        choice = input('Select a profile number or option: ')
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(user_data["profiles"]):
                selected_profile = user_data["profiles"][choice_num - 1]
                print(f'\nSwitched to profile: {selected_profile["profile_name"]}')
                return selected_profile
            elif choice_num == len(user_data["profiles"]) + 1:
                create_new_profile(user)
                user_data = get_user_data(user)  # Refresh user data
            elif choice_num == len(user_data["profiles"]) + 2:
                delete_profile(user)
                user_data = get_user_data(user)  # Refresh user data
            elif choice_num == len(user_data["profiles"]) + 3:
                print('Logging out...')
                return None
            else:
                print('Invalid choice. Please try again.')
        except ValueError:
            print('Invalid input. Please enter a number.')

def create_new_profile(user):
    """Create a new profile for the user"""
    users = load_users()
    
    profile_name = input('Enter profile name: ')
    if not profile_name.strip():
        print('Profile name cannot be empty!')
        return
    
    # Check for duplicate profile name
    user_data = get_user_data(user)
    if user_data and any(p['profile_name'] == profile_name for p in user_data.get('profiles', [])):
        print(f'Profile "{profile_name}" already exists!')
        return
    
    currency = input('Enter currency (default is USD): ')
    if not currency.strip():
        currency = "USD"
    
    new_profile = create_profile_data(profile_name, currency)
    
    for u in users:
        if u["name"] == user:
            u["profiles"].append(new_profile)
            save_users(users)
            print(f'Profile "{profile_name}" created successfully!')
            return
    
    print('Error: User not found!')

def delete_profile(user):
    """Delete a profile"""
    user_data = get_user_data(user)
    
    if len(user_data["profiles"]) <= 1:
        print('Cannot delete the last profile! You must have at least one profile.')
        return
    
    print('\nSelect profile to delete:')
    for idx, profile in enumerate(user_data["profiles"], 1):
        print(f'{idx}. {profile["profile_name"]} (Currency: {profile["currency"]})')
    
    choice = input('Enter profile number to delete (or 0 to cancel): ')
    
    try:
        choice_num = int(choice)
        if choice_num == 0:
            return
        if 1 <= choice_num <= len(user_data["profiles"]):
            # Confirm deletion
            password = getpass.getpass('Enter your password to confirm deletion:  ')
            users = load_users()
            for u in users:
                if u["name"] == user and verify_password(password, u["password"]):
                    profile_to_delete = u["profiles"][choice_num - 1]
                    profile_id = profile_to_delete["profile_id"]
                    
                    # Delete associated transactions
                    delete_profile_transactions(profile_id)
                    
                    # Remove profile
                    del u["profiles"][choice_num - 1]
                    save_users(users)
                    print(f'Profile "{profile_to_delete["profile_name"]}" deleted successfully!')
                    return
            print('Authentication failed! Profile not deleted.')
        else:
            print('Invalid choice.')
    except ValueError:
        print('Invalid input. Please enter a number.')

def delete_profile_transactions(profile_id):
    """Delete all transactions for a specific profile"""
    if not os.path.exists(TRANSACTIONS_FILE): # defensive programming
        return
    
    all_transactions = []
    with open(TRANSACTIONS_FILE, 'r') as csvfile: # read all transactions
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {key.strip(): value for key, value in row.items()}
            if cleaned_row.get('profile_id') != profile_id:
                all_transactions.append(cleaned_row)
    
    with open(TRANSACTIONS_FILE, 'w', newline='') as csvfile: # rewrite file
        fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 'category', 'date', 'description', 'payment_method']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for txn in all_transactions:
            writer.writerow(txn) 

def HomePage(user, profile):
    while True:
        print('\n' + '='*50)
        print('Welcome to your Expense Tracker Home Page!')
        print(f'User: {user} | Profile: {profile["profile_name"]} | Currency: {profile["currency"]}')
        print('='*50)
        print('1. Transactions')
        print('2. Reports')
        print('3. Switch Profile')
        print('4. Logout')
        print('='*50)
        choice = input('Please select an option: ')
        
        if choice == '1':
            Transactions(user, profile)
        elif choice == '2':
            Reports(user, profile)
        elif choice == '3':
            print('Switching profile...')
            new_profile = profile_menu(user)  # ✅ Capture the returned profile
            if new_profile:  # ✅ Check if a profile was selected
                profile = new_profile  # ✅ Update the current profile
            else:
                # User chose to logout from profile menu
                return 'logout'
        elif choice == '4':
            print('Logging out...')
            return 'logout'
        else:
            print('Invalid choice. Please try again.')

def Transactions(user, profile):
    while True:
        print('\n' + '='*50) 
        print(f'Transactions Page - Profile: {profile["profile_name"]}')
        print('='*50)
        print('1. Add Expense') 
        print('2. Add Income')
        print('3. View All Transactions')
        print('4. Search / Filter Transactions')
        print('5. Edit or Delete Transaction')
        print('6. Back to Home Page')
        choice = input('Please select an option: ')
        
        if choice == '1':
            if add_transaction(user, profile, 'expense'):
                print('Expense added successfully!')
            else:
                print('Failed to add expense.')
        elif choice == '2':
            if add_transaction(user, profile, 'income'):
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
                        cleaned_row = {key.strip(): value for key, value in row.items()}
                        if cleaned_row.get('profile_id') == profile['profile_id']:
                            display_transaction(cleaned_row, profile)
                            found = True
                    if not found:
                        print('You have no transactions in this profile!')
        elif choice == '4':
            print('Search / Filter Transactions Page')
            # Placeholder for search/filter functionality
        elif choice == '5':
            edit_or_delete_transaction(user, profile)
        elif choice == '6':
            print('Returning to Home Page...')
            break
        else:
            print('Invalid choice. Please try again.')

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

def display_transaction(txn, profile):
    """Display a transaction in a readable format"""
    print(f"\nID: {txn['transaction_id']}")
    print(f"Type: {txn['type'].capitalize()}")
    print(f"Amount: {txn['amount']} {profile['currency']}")
    print(f"Category: {txn['category']}")
    print(f"Date: {txn['date']}")
    print(f"Description: {txn['description']}")
    print(f"Payment: {txn['payment_method']}")
    print('-' * 40)

def Reports(user, profile):     
    print(f'Reports Page - Profile: {profile["profile_name"]}')
    # Placeholder for reports functionality

if __name__ == '__main__':
    monthly_backup()  
    while True:
        choice = menu()
        if choice == '1':
            user = login()
            if user:
                while True:
                    profile = profile_menu(user) # Get selected profile
                    if profile is None: # User chose to logout
                        break
                    result = HomePage(user, profile) # Call HomePage and capture result
                    if result == 'logout':
                        break
          
        elif choice == '2':
            user = register()
            if user:
                while True:
                    profile = profile_menu(user)
                    if profile is None:
                        break
                    result = HomePage(user, profile)
                    if result == 'logout':
                        break
        elif choice == '3':
            print('Exiting the program. Goodbye!')
            break
        else:
            print('Invalid choice. Please try again.')
