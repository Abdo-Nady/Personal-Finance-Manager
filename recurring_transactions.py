import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
import storage
from utils import clear_screen , PrintMesg , PrintMenu 
import utils
import csv

RECURRING_FILE = os.path.join(os.path.dirname(__file__), "data", "recurring_transactions.json")

def load_recurring_transactions():
    """Load recurring transactions from JSON"""
    if not os.path.exists(RECURRING_FILE):
        return []
    try:
        with open(RECURRING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (ValueError, json.JSONDecodeError):
        return []

def save_recurring_transactions(recurring_list):
    """Save recurring transactions to JSON"""
    os.makedirs(os.path.dirname(RECURRING_FILE), exist_ok=True)
    with open(RECURRING_FILE, 'w', encoding='utf-8') as f:
        json.dump(recurring_list, f, ensure_ascii=False, indent=4)

def create_recurring_transaction(username, profile_id, name, trans_type, amount, 
                                 repeat_interval_days, start_date=None, end_date=None):
    """Create new recurring transaction"""
    recurring_list = load_recurring_transactions()
    
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    if not utils.validate_date(start_date) or (end_date and not utils.validate_date(end_date)):
        return None
    
    new_recurring = {
        "recurring_id": str(uuid.uuid4()),
        "username": username,
        "profile_id": profile_id,
        "name": name.strip(),
        "type": trans_type.lower(),
        "amount": str(amount),
        "repeat_interval_days": int(repeat_interval_days),
        "start_date": start_date,
        "next_date": start_date,
        "end_date": end_date,
        "status": "Active",
        "last_executed": None
    }
    
    recurring_list.append(new_recurring)
    save_recurring_transactions(recurring_list)
    return new_recurring

def get_user_recurring_transactions(username, profile_id=None, status=None):
    """Get filtered recurring transactions"""
    all_recurring = load_recurring_transactions()
    filtered = [r for r in all_recurring if r['username'] == username]
    
    if profile_id:
        filtered = [r for r in filtered if r['profile_id'] == profile_id]
    if status:
        filtered = [r for r in filtered if r['status'] == status]
    
    return filtered

def execute_due_recurring_transactions(): 
    """Execute all due recurring transactions"""
    recurring_list = load_recurring_transactions()
    today = datetime.now().strftime("%Y-%m-%d")
    executed_count = 0
    
    for recurring in recurring_list:
        if recurring['status'] != 'Active' or recurring['next_date'] > today:
            continue
        
        if _execute_single_recurring(recurring):
            executed_count += 1
            next_dt = datetime.strptime(recurring['next_date'], "%Y-%m-%d")
            next_dt += timedelta(days=recurring['repeat_interval_days'])
            recurring['next_date'] = next_dt.strftime("%Y-%m-%d")
            recurring['last_executed'] = today
            
            if recurring['end_date'] and recurring['next_date'] > recurring['end_date']:
                recurring['status'] = 'Completed'
    
    save_recurring_transactions(recurring_list)
    return executed_count

def _execute_single_recurring(recurring):
    """Execute single recurring transaction"""
    try:
        users = storage.load_users()
        user = next((u for u in users if u['name'] == recurring['username']), None)
        if not user:
            return False
        
        profile = next((p for p in user.get('profiles', []) 
                       if p['profile_id'] == recurring['profile_id']), None)
        if not profile:
            return False
        transaction_data = {
            'transaction_id': f'TXN{int(datetime.now().timestamp())}',
            'user': recurring['username'],
            'profile_id': recurring['profile_id'],
            'type': recurring['type'],
            'amount': recurring['amount'],
            'category': f"Recurring: {recurring['name']}",
            'date': recurring['next_date'],
            'description': 'Auto-generated',
            'payment_method': 'Recurring'
        }
        
        os.makedirs(os.path.dirname(storage.TRANSACTIONS_FILE), exist_ok=True) # ensure data dir
        fieldnames = ['transaction_id', 'user', 'profile_id', 'type', 'amount', 
                      'category', 'date', 'description', 'payment_method']
        
        file_exists = os.path.exists(storage.TRANSACTIONS_FILE)
        with open(storage.TRANSACTIONS_FILE, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            if not file_exists or os.stat(storage.TRANSACTIONS_FILE).st_size == 0:
                writer.writeheader()
            writer.writerow(transaction_data)
                
      
        return True
    except Exception as e:
        print(f"Error executing recurring transaction: {e}")
        return False

def update_recurring_status(recurring_id, new_status): 
    """Update recurring transaction status (Active/Paused/Completed)"""
    recurring_list = load_recurring_transactions()
    recurring = next((r for r in recurring_list if r['recurring_id'] == recurring_id), None)
    
    if not recurring or recurring['status'] == 'Completed':
        return False
    
    recurring['status'] = new_status
    save_recurring_transactions(recurring_list)
    return True

def update_recurring_transaction(recurring_id, **updates):
    """Update recurring transaction fields"""
    recurring_list = load_recurring_transactions()
    recurring = next((r for r in recurring_list if r['recurring_id'] == recurring_id), None)
    
    if not recurring:
        return False
    
    allowed = ['name', 'amount', 'repeat_interval_days', 'end_date']
    for field, value in updates.items():
        if field in allowed:
            if field == 'amount':
                recurring[field] = str(value)
            elif field == 'end_date' and value and not utils.validate_date(value):
                return False
            else:
                recurring[field] = value
    
    save_recurring_transactions(recurring_list)
    return True

def delete_recurring_transaction(recurring_id):
    """Delete recurring transaction"""
    recurring_list = load_recurring_transactions()
    recurring = next((r for r in recurring_list if r['recurring_id'] == recurring_id), None)
    
    if not recurring:
        return False
    
    recurring_list.remove(recurring)
    save_recurring_transactions(recurring_list)
    return True

def get_recurring_history(recurring_id):
    """Get execution history for recurring transaction"""
    recurring_list = load_recurring_transactions()
    recurring = next((r for r in recurring_list if r['recurring_id'] == recurring_id), None)
    
    if not recurring:
        return []
    
    if not os.path.exists(storage.TRANSACTIONS_FILE):
        return []
    
    history = []
        
    try:
        with open(storage.TRANSACTIONS_FILE, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cleaned = {k.strip(): v.strip() for k, v in row.items()}
                if (cleaned.get('user') == recurring['username'] and 
                    cleaned.get('profile_id') == recurring['profile_id'] and
                    f"Recurring: {recurring['name']}" in cleaned.get('category', '')):
                    history.append(cleaned)
    except Exception:
        return []
    
    return history

def recurring_transactions_menu(username, profile):
    """Main recurring transactions menu"""
    while True:
        
        
        options = [
            "Create New", "View All", "Pause/Resume",
            "Edit", "Delete", "View History",
            "Execute Due Now", "Back"
        ]
          
        PrintMenu('Recurring Transactions Menu', options)
            
      
       
        choice = input("Choose: ").strip()
        
        actions = {
            '1': lambda: _create_ui(username, profile),
            '2': lambda: _view_ui(username, profile),
            '3': lambda: _pause_resume_ui(username, profile),
            '4': lambda: _edit_ui(username, profile),
            '5': lambda: _delete_ui(username, profile),
            '6': lambda: _history_ui(username, profile),
            '7': lambda: print(f"\nExecuted {execute_due_recurring_transactions()} recurring transaction(s)"),
            '8': lambda: None
        }
        
        if choice == '8':
            break
        actions.get(choice, lambda: print("\nInvalid choice!"))() 

def _create_ui(username, profile):
    """Create recurring transaction UI"""
    name = input("Name: ").strip()
    if not name:
        print("\nName is required!")
        return
    
    
    
    print("1. Income  2. Expense")
    trans_type = 'income' if input("Type: ").strip() == '1' else 'expense'
    
    try:
        amount = Decimal(input("Amount: ").strip())
        if amount <= 0:
            raise ValueError
    except:
        print("\nInvalid amount!")
        return
    
    print("1. Daily  2. Weekly  3. Bi-weekly  4. Monthly  5. Custom")
    interval = input("Interval: ").strip()
    intervals = {'1': 1, '2': 7, '3': 14, '4': 30}
    
    if interval in intervals:
        days = intervals[interval]
    elif interval == '5':
        try:
            days = int(input("Days: ").strip())
            if days <= 0:
                raise ValueError
        except:
            print("\nInvalid interval!")
            return
    else:
        print("\nInvalid choice!")
        return
    
    start = input("Start (YYYY-MM-DD) [Enter=today]: ").strip() or None
    end = input("End date? (YYYY-MM-DD) [Enter=none]: ").strip() or None
    
    result = create_recurring_transaction(username, profile['profile_id'], name, 
                                               trans_type, amount, days, start, end)
    print("\nRecurring transaction created successfully!" if result else "\nFailed to create recurring transaction!")

def _view_ui(username, profile):
    """View recurring transactions"""
    items = get_user_recurring_transactions(username, profile['profile_id'])
    if not items:
        print("\nNo recurring transactions found.")
        return
    
    print(f"\n{'#':<3} {'Name':<20} {'Type':<8} {'Amount':<10} {'Days':<6} {'Next':<12} {'Status':<10}")
    print("-" * 75)
    for i, r in enumerate(items, 1):
        print(f"{i:<3} {r['name']:<20} {r['type']:<8} {r['amount']:<10} {r['repeat_interval_days']:<6} {r['next_date']:<12} {r['status']:<10}")
        
    input("\nPress Enter to continue...")

def _select_item(username, profile, action_name):
    """Helper to select a recurring transaction"""
    items = get_user_recurring_transactions(username, profile['profile_id'])
    if not items:
        print("\nNo recurring transactions found.")
        return None
    
    _view_ui(username, profile)
    try:
        idx = int(input(f"\nSelect # to {action_name}: ").strip()) - 1
        if 0 <= idx < len(items):
            return items[idx]
    except:
        pass
    print("\nInvalid selection!")
    return None

def _pause_resume_ui(username, profile):
    """Pause/Resume UI"""
    item = _select_item(username, profile, "pause/resume")
    if not item:
        return
    
    if item['status'] == 'Active':
        update_recurring_status(item['recurring_id'], 'Paused')
        print("\nRecurring transaction paused.")
    elif item['status'] == 'Paused':
        update_recurring_status(item['recurring_id'], 'Active')
        print("\nRecurring transaction resumed.")
    else:
        print("\nCannot modify completed transaction.")

def _edit_ui(username, profile):
    """Edit UI"""
    item = _select_item(username, profile, "edit")
    if not item:
        return
    
    print("\n1. Name  2. Amount  3. Interval Days  4. End Date")
    choice = input("Edit: ").strip()
    
    updates = {}
    try:
        if choice == '1':
            new_name = input(f"New name [{item['name']}]: ").strip()
            if new_name:
                updates['name'] = new_name
        elif choice == '2':
            updates['amount'] = Decimal(input(f"New amount [{item['amount']}]: ").strip())
        elif choice == '3':
            updates['repeat_interval_days'] = int(input(f"New interval [{item['repeat_interval_days']}]: ").strip())
        elif choice == '4':
            updates['end_date'] = input(f"New end date [{item['end_date']}]: ").strip() or None
        
        if updates and update_recurring_transaction(item['recurring_id'], **updates):
            print("\nRecurring transaction updated successfully!")
        else:
            print("\nFailed to update recurring transaction!")
    except:
        print("\nInvalid input!")

def _delete_ui(username, profile):
    """Delete UI"""
    item = _select_item(username, profile, "delete")
    if not item:
        return
    
    if input(f"\nDelete '{item['name']}'? (yes/no): ").lower() == 'yes':
        if delete_recurring_transaction(item['recurring_id']):
            print("\nRecurring transaction deleted successfully!")
        else:
            print("\nFailed to delete recurring transaction!")

def _history_ui(username, profile):
    """History UI"""
    item = _select_item(username, profile, "view history")
    if not item:
        return
    
    history = get_recurring_history(item['recurring_id'])
    if not history:
        print(f"\nNo execution history found for '{item['name']}'")
        return
    
    print(f"\n--- Execution History: {item['name']} ---")
    print(f"{'Date':<12} {'Amount':<10} {'Description':<30}")
    print("-" * 55)
    for t in history:
        print(f"{t['date']:<12} {t['amount']:<10} {t.get('description', ''):<30}")
    print(f"\nTotal executions: {len(history)}")