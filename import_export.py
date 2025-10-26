import csv
import os
import datetime
from decimal import Decimal
from storage import TRANSACTIONS_FILE
from utils import clear_screen

def export_transactions(user, profile):
    """Export all transactions for the current profile to a CSV file"""
    # Check if transactions file exists
    if not os.path.exists(TRANSACTIONS_FILE):
        print('\nNo transactions found to export!')
        return
    
    # Read and filter transactions for this profile
    profile_transactions = []
    with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cleaned_row = {key.strip(): value for key, value in row.items()}
            if cleaned_row.get('profile_id') == profile['profile_id']:
                profile_transactions.append(cleaned_row)
    
    # Validate that we have transactions to export
    if not profile_transactions:
        print('\nNo transactions found for this profile!')
        return
    
    # Generate timestamped filename
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"export_{profile['profile_name']}_{timestamp}.csv"
    
    # Write transactions to CSV file
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                         'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for txn in profile_transactions:
                writer.writerow(txn)
        
        print(f'\n✅ Successfully exported {len(profile_transactions)} transactions to "{filename}"')
        print(f'   Location: {os.path.abspath(filename)}')
    except Exception as e:
        print(f'\nError exporting transactions: {e}')


def import_transactions(user, profile):
    """Import transactions from a CSV file with validation and duplicate detection"""
    print('\n' + '='*60)
    print('Import Transactions from CSV')
    print('='*60)
    
    # Get filename from user
    filename = input('Enter the CSV filename to import: ').strip()
    
    if not os.path.exists(filename):
        print(f'\nFile "{filename}" not found!')
        return
    
    # Select import mode
    print('\nImport Options:')
    print('1. Skip duplicates (recommended)')
    print('2. Import all (may create duplicates)')
    
    import_mode = input('Select option: ').strip()
    skip_duplicates = import_mode == '1'
    
    # Load existing transaction IDs if skipping duplicates
    existing_txn_ids = set()
    if skip_duplicates and os.path.exists(TRANSACTIONS_FILE):
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_txn_ids.add(row.get('transaction_id', '').strip())
    
    # Read and validate import file
    imported_transactions = []
    skipped_count = 0
    error_count = 0
    
    try:
        with open(filename, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            
            # Validate CSV headers
            required_fields = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                             'category', 'date', 'description', 'payment_method']
            if not all(field in reader.fieldnames for field in required_fields):
                print(f'\nInvalid CSV format! Missing required fields.')
                print(f'   Required: {", ".join(required_fields)}')
                return
            
            # Process each row
            for line_num, row in enumerate(reader, start=2):
                cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                
                # Validate transaction
                validation_result = validate_transaction(cleaned_row, line_num)
                if (validation_result == 'valid' and 
                    cleaned_row.get('user') == user and 
                    cleaned_row.get('profile_id') == profile['profile_id']):
                    
                    # Check for duplicates
                    if skip_duplicates and cleaned_row['transaction_id'] in existing_txn_ids:
                        skipped_count += 1
                        continue
                    
                    imported_transactions.append(cleaned_row)
                elif validation_result != 'valid':
                    # Only print errors for validation issues, not user/profile mismatch
                    print(f'   ⚠️  Line {line_num}: {validation_result}')
                    error_count += 1
    
    except Exception as e:
        print(f'\nError reading file: {e}')
        return
    
    # Validate that we have transactions to import
    if not imported_transactions:
        print(f'\n⚠️  No valid transactions to import!')
        if skipped_count > 0:
            print(f'   Skipped {skipped_count} duplicate(s)')
        if error_count > 0:
            print(f'   Found {error_count} error(s)')
        return
    
    # Display summary and get confirmation
    print(f'\n📊 Import Summary:')
    print(f'   Valid transactions: {len(imported_transactions)}')
    if skipped_count > 0:
        print(f'   Skipped duplicates: {skipped_count}')
    if error_count > 0:
        print(f'   Errors found: {error_count}')
    
    confirm = input('\nProceed with import? (yes/no): ').strip().lower()
    if confirm != 'yes':
        print('Import cancelled.')
        return
    
    # Append transactions to file
    try:
        file_exists = os.path.exists(TRANSACTIONS_FILE)
        
        with open(TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                         'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists or os.stat(TRANSACTIONS_FILE).st_size == 0:
                writer.writeheader()
            
            for txn in imported_transactions:
                writer.writerow(txn)
        
        print(f'\n✅ Successfully imported {len(imported_transactions)} transactions!')
    except Exception as e:
        print(f'\nError writing transactions: {e}')


def validate_transaction(txn, line_num):
    """Validate a single transaction row from imported CSV data"""
    # Check required fields
    required_fields = ['transaction_id', 'type', 'amount', 'category', 
                      'date', 'description', 'payment_method']
    
    for field in required_fields:
        if not txn.get(field):
            return f'Missing {field}'
    
    # Validate transaction type
    if txn['type'].lower() not in ['income', 'expense']:
        return f'Invalid type "{txn["type"]}" (must be income or expense)'
    
    # Validate amount
    try:
        amount = Decimal(txn['amount'])
        if amount <= 0:
            return f'Amount must be greater than 0'
    except:
        return f'Invalid amount "{txn["amount"]}"'
    
    # Validate date format
    try:
        datetime.datetime.strptime(txn['date'], '%Y-%m-%d')
    except ValueError:
        return f'Invalid date format "{txn["date"]}" (use YYYY-MM-DD)'
    
    return 'valid'


def ImportExport(user, profile):
    """Main menu for import/export operations"""
    while True:
        clear_screen()
        print('\n' + '='*60)
        print(f'Import/Export - Profile: {profile["profile_name"]}')
        print('='*60)
        print('1. Export Transactions to CSV')
        print('2. Import Transactions from CSV')
        print('3. Back to Home Page')
        print('='*60)
        
        choice = input('Select an option: ').strip()
        
        if choice == '1':
            export_transactions(user, profile)
        elif choice == '2':
            import_transactions(user, profile)
        elif choice == '3':
            break
        else:
            print('Invalid choice. Please try again.')