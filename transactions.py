import os
import csv
import datetime
from decimal import Decimal
import getpass
from utils import verify_password, clear_screen
from storage import load_users, TRANSACTIONS_FILE, ensure_data_directory
from recurring_transactions import recurring_transactions_menu


def add_transaction(user, profile, type_):
    """Add a new transaction (income or expense)"""
    transaction_id = f'TXN{int(datetime.datetime.now().timestamp())}'
    
    # Amount input
    amount_input = input('Enter amount: ').strip()
    try:
        amount = Decimal(amount_input)
        if amount <= 0:
            print('\nAmount must be greater than 0!')
            input('\nPress Enter to continue...')
            return False
    except:
        print('\nInvalid amount. Please enter a numeric value.')
        input('\nPress Enter to continue...')
        return False
    
    # Category input
    category = input('Enter category: ').strip()
    if not category:
        print('\nCategory cannot be empty!')
        input('\nPress Enter to continue...')
        return False
    
    # Date input
    date = input('Enter date (YYYY-MM-DD): ').strip()
    try:
        datetime.datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        print('\nInvalid date format. Please use YYYY-MM-DD.')
        input('\nPress Enter to continue...')
        return False
    
    # Description input
    description = input('Enter description: ').strip()
    
    # Payment method input
    payment_method = input('Enter payment method: ').strip()
    if not payment_method:
        print('\nPayment method cannot be empty!')
        input('\nPress Enter to continue...')
        return False
    
    # Ensure data directory exists
    ensure_data_directory()
    
    file_exists = os.path.exists(TRANSACTIONS_FILE)
    
    try:
        with open(TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                         'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists or os.stat(TRANSACTIONS_FILE).st_size == 0:
                writer.writeheader()
            
            writer.writerow({
                'transaction_id': transaction_id,
                'user': user,
                'profile_id': profile['profile_id'],
                'type': type_,
                'amount': str(amount),
                'category': category.strip(),
                'date': date,
                'description': description,
                'payment_method': payment_method.strip()
            })
        return True
    except Exception as e:
        print(f'\nError writing to file: {e}')
        input('\nPress Enter to continue...')
        return False


def load_all_transactions():
    """Load all transactions from CSV file"""
    if not os.path.exists(TRANSACTIONS_FILE):
        return []
    
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                transactions.append(cleaned_row)
    except Exception as e:
        print(f'\nError reading transactions: {e}')
    
    return transactions


def save_all_transactions(transactions):
    """Save all transactions to CSV file"""
    ensure_data_directory()
    
    try:
        with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                         'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for txn in transactions:
                writer.writerow(txn)
        return True
    except Exception as e:
        print(f'\nError saving transactions: {e}')
        return False


def edit_or_delete_transaction(user, profile):
    """Edit or delete a transaction"""
    print('\n--- All Your Transactions ---')
    
    all_transactions = load_all_transactions()
    
    if not all_transactions:
        print('No transactions found!')
        input('\nPress Enter to continue...')
        return
    
    # Filter transactions for current profile
    profile_transactions = [
        txn for txn in all_transactions 
        if txn.get('profile_id') == profile['profile_id']
    ]
    
    if not profile_transactions:
        print('You have no transactions in this profile!')
        input('\nPress Enter to continue...')
        return
    
    # Display transactions
    for txn in profile_transactions:
        display_transaction(txn, profile)
    
    # Get transaction ID
    txn_id = input('\nEnter the Transaction ID to edit or delete: ').strip()
    if not txn_id:
        print('\nTransaction ID cannot be empty!')
        input('\nPress Enter to continue...')
        return
    
    # Find target transaction
    target_txn = None
    target_index = -1
    for i, txn in enumerate(all_transactions):
        if (txn['transaction_id'] == txn_id and 
            txn.get('profile_id') == profile['profile_id']):
            target_txn = txn
            target_index = i
            break
    
    if not target_txn:
        print('\nTransaction not found in this profile!')
        input('\nPress Enter to continue...')
        return
    
    # Ask for action
    action = input('\nEnter "e" to edit or "d" to delete: ').lower().strip()
    
    if action == 'e':
        print('\n--- Edit Transaction (press Enter to keep current value) ---')
        
        # Edit amount
        new_amount = input(f'Amount (current: {target_txn["amount"]}): ').strip()
        if new_amount:
            try:
                validated_amount = Decimal(new_amount)
                if validated_amount <= 0:
                    print('Amount must be greater than 0! Keeping current value.')
                else:
                    target_txn['amount'] = str(validated_amount)
            except:
                print('Invalid amount! Keeping current value.')
        
        # Edit category
        new_category = input(f'Category (current: {target_txn["category"]}): ').strip()
        if new_category:
            target_txn['category'] = new_category
        
        # Edit date
        new_date = input(f'Date (current: {target_txn["date"]}): ').strip()
        if new_date:
            try:
                datetime.datetime.strptime(new_date, '%Y-%m-%d')
                target_txn['date'] = new_date
            except ValueError:
                print('Invalid date format! Keeping current value.')
        
        # Edit description
        new_description = input(f'Description (current: {target_txn["description"]}): ').strip()
        if new_description:
            target_txn['description'] = new_description
        
        # Edit payment method
        new_payment = input(f'Payment method (current: {target_txn["payment_method"]}): ').strip()
        if new_payment:
            target_txn['payment_method'] = new_payment
        
        # Save changes
        all_transactions[target_index] = target_txn
        if save_all_transactions(all_transactions):
            print('\nTransaction updated successfully!')
        else:
            print('\nFailed to update transaction!')
        
    elif action == 'd':
        # Verify password before deletion
        password = getpass.getpass('\nEnter your password to confirm deletion: ')
        users = load_users()
        
        authenticated = False
        for u in users:
            if u["name"] == user and verify_password(password, u["password"]):
                authenticated = True
                break
        
        if not authenticated:
            print('\nAuthentication failed! Transaction not deleted.')
            input('\nPress Enter to continue...')
            return
        
        # Remove transaction
        all_transactions.pop(target_index)
        
        if save_all_transactions(all_transactions):
            print('\nTransaction deleted successfully!')
        else:
            print('\nFailed to delete transaction!')
        
    else:
        print('\nInvalid action!')
    
    input('\nPress Enter to continue...')


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


def search_filter_transactions(profile):
    """Search and filter transactions for the given profile"""
    if not os.path.exists(TRANSACTIONS_FILE):
        print("\nNo transactions file found.")
        input('\nPress Enter to continue...')
        return

    print('\n' + '='*60)
    print('Search / Filter Transactions')
    print('='*60)
    print("You can leave any field empty to skip that filter.\n")

    keyword = input("Keyword (category or description): ").strip().lower()
    date_from = input("From date (YYYY-MM-DD): ").strip()
    date_to = input("To date (YYYY-MM-DD): ").strip()
    min_amount = input("Minimum amount: ").strip()
    max_amount = input("Maximum amount: ").strip()
    txn_type = input("Type (income / expense): ").strip().lower()
    sort_by = input("Sort by (date / amount): ").strip().lower()
    sort_order = input("Order (asc / desc): ").strip().lower() or "asc"

    results = []

    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                row = {k.strip(): v.strip() for k, v in row.items()}
                if row.get("profile_id") != profile["profile_id"]:
                    continue

                try:
                    txn_date = datetime.datetime.strptime(row["date"], "%Y-%m-%d")
                    txn_amount = Decimal(row["amount"])
                except:
                    continue

                # Apply filters
                if keyword and not (keyword in row["description"].lower() or keyword in row["category"].lower()):
                    continue
                    
                if date_from:
                    try:
                        if txn_date < datetime.datetime.strptime(date_from, "%Y-%m-%d"):
                            continue
                    except ValueError:
                        print("Invalid 'from' date format, skipping filter.")
                        
                if date_to:
                    try:
                        if txn_date > datetime.datetime.strptime(date_to, "%Y-%m-%d"):
                            continue
                    except ValueError:
                        print("Invalid 'to' date format, skipping filter.")
                        
                if min_amount:
                    try:
                        if txn_amount < Decimal(min_amount):
                            continue
                    except:
                        print("Invalid minimum amount format.")
                        
                if max_amount:
                    try:
                        if txn_amount > Decimal(max_amount):
                            continue
                    except:
                        print("Invalid maximum amount format.")
                        
                if txn_type and row["type"].lower() != txn_type:
                    continue

                results.append(row)
    except Exception as e:
        print(f"\nError reading transactions: {e}")
        input('\nPress Enter to continue...')
        return

    # Sort results
    if sort_by in ["date", "amount"]:
        reverse = sort_order == "desc"
        if sort_by == "date":
            results.sort(key=lambda x: x["date"], reverse=reverse)
        elif sort_by == "amount":
            results.sort(key=lambda x: Decimal(x["amount"]), reverse=reverse)

    if not results:
        print("\nNo transactions match your filters.")
        input('\nPress Enter to continue...')
        return

    # Display results
    print('\n' + '='*60)
    print(f"{'Date':<12} | {'Type':<7} | {'Category':<15} | {'Amount':<12} | {'Description'}")
    print('-'*60)
    for txn in results:
        print(f"{txn['date']:<12} | {txn['type'].capitalize():<7} | {txn['category']:<15} | "
              f"{txn['amount']:>8} {profile['currency']:<3} | {txn['description']}")
    print('-'*60)
    print(f"Total: {len(results)} record(s)")
    
    input('\nPress Enter to continue...')


def view_all_transactions(profile):
    """View all transactions for current profile"""
    print('\n--- All Transactions ---')
    
    transactions = load_all_transactions()
    
    if not transactions:
        print('No transactions found!')
        input('\nPress Enter to continue...')
        return
    
    profile_transactions = [
        txn for txn in transactions 
        if txn.get('profile_id') == profile['profile_id']
    ]
    
    if not profile_transactions:
        print('You have no transactions in this profile!')
        input('\nPress Enter to continue...')
        return
    
    for txn in profile_transactions:
        display_transaction(txn, profile)
    
    print(f'\nTotal: {len(profile_transactions)} transaction(s)')
    input('\nPress Enter to continue...')


def Transactions(user, profile):
    """Main transactions menu"""
    while True:
        clear_screen()
        print('\n' + '='*50) 
        print(f'Transactions Page - Profile: {profile["profile_name"]}')
        print('='*50)
        print('1. Add Expense') 
        print('2. Add Income')
        print('3. Add Recurring / Scheduled Transaction')
        print('4. View All Transactions')
        print('5. Search / Filter Transactions')
        print('6. Edit or Delete Transaction')
        print('7. Back to Home Page')
        print('='*50)
        
        choice = input('Please select an option ✎𓂃  ').strip()
        
        if choice == '1':
            if add_transaction(user, profile, 'expense'):
                print('\nExpense added successfully!')
                input('\nPress Enter to continue...')
            else:
                print('\nFailed to add expense.')
                
        elif choice == '2':
            if add_transaction(user, profile, 'income'):
                print('\nIncome added successfully!')
                input('\nPress Enter to continue...')
            else:
                print('\nFailed to add income.')
                
        elif choice == '3':
            recurring_transactions_menu(user, profile)
            
        elif choice == '4':
            view_all_transactions(profile)
            
        elif choice == '5':
            search_filter_transactions(profile)

        elif choice == '6':
            edit_or_delete_transaction(user, profile)
            
        elif choice == '7':
            print('\nReturning to Home Page...')
            break
            
        else:
            print('\nInvalid choice. Please try again.')
            input('\nPress Enter to continue...')