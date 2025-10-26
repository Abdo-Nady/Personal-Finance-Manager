import os
import json
import shutil
import datetime
import csv

USERS_FILE = "data/users.json"
TRANSACTIONS_FILE = "data/transaction.csv"
BACKUP_DIR = "backups"
LAST_BACKUP_FILE = "last_backup.txt"


def ensure_data_directory():
    """Ensure data directory exists"""
    os.makedirs("data", exist_ok=True)


def load_users():
    """Load users from JSON file"""
    ensure_data_directory()
    if not os.path.exists(USERS_FILE):        
        return []
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f: 
            return json.load(f) 
    except (json.JSONDecodeError, IOError) as e:
        print(f"Warning: Error loading users - {e}")
        return []

    
def save_users(users):
    """Save users to JSON file with atomic write"""
    ensure_data_directory()
    try:
        # Write to temp file first for atomicity
        temp_file = USERS_FILE + '.tmp'
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4, ensure_ascii=False)
        
        # Atomic rename
        os.replace(temp_file, USERS_FILE)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False


def delete_profile_transactions(profile_id):
    """Delete all transactions for a specific profile"""
    if not os.path.exists(TRANSACTIONS_FILE):
        return
    
    try:
        all_transactions = []
        
        # Read all transactions except those from the deleted profile
        with open(TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned_row = {key.strip(): value.strip() for key, value in row.items()}
                if cleaned_row.get('profile_id') != profile_id:
                    all_transactions.append(cleaned_row)
        
        # Write back remaining transactions
        with open(TRANSACTIONS_FILE, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                         'category', 'date', 'description', 'payment_method']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for txn in all_transactions:
                writer.writerow(txn)
        
        return True
    except Exception as e:
        print(f"Error deleting profile transactions: {e}")
        return False


def should_backup():
    """Check if we need to backup this month"""
    if not os.path.exists(LAST_BACKUP_FILE):
        return True
    
    try:
        with open(LAST_BACKUP_FILE, 'r', encoding='utf-8') as f:
            last_backup = f.read().strip()
            current_month = datetime.datetime.now().strftime('%Y-%m')
            return last_backup != current_month
    except Exception:
        return True


def monthly_backup():
    """Create backup once per month"""
    if not should_backup():
        return
    
    timestamp = datetime.datetime.now().strftime('%Y-%m')  # YYYY-MM format
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    try:
        backup_count = 0
        
        # Backup users file
        if os.path.exists(USERS_FILE):
            shutil.copy2(USERS_FILE, f"{BACKUP_DIR}/users_{timestamp}.json")
            backup_count += 1
        
        # Backup transactions file
        if os.path.exists(TRANSACTIONS_FILE):
            shutil.copy2(TRANSACTIONS_FILE, f"{BACKUP_DIR}/transaction_{timestamp}.csv")
            backup_count += 1
        
        if backup_count > 0:
            # Update last backup date
            with open(LAST_BACKUP_FILE, 'w', encoding='utf-8') as f:
                f.write(datetime.datetime.now().strftime('%Y-%m'))
            
            print(f"\n{'='*50}")
            print(f"Monthly backup created successfully! ({timestamp})")
            print(f"{'='*50}\n")
            
       
            
    except Exception as e:
        print(f"Warning: Backup failed - {e}")


