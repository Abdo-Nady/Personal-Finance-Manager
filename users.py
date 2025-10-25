import uuid
import getpass
from storage import load_users, save_users
from utils import hash_password, verify_password
from storage import delete_profile_transactions

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
