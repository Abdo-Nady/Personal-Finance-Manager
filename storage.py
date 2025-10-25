import os
import json
import shutil
import datetime
import csv

USERS_FILE = "data/users.json"
TRANSACTIONS_FILE = "data/transaction.csv"
BACKUP_DIR = "backups"
LAST_BACKUP_FILE = "last_backup.txt"


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


