import uuid
import getpass
from storage import load_users, save_users
from utils import PrintMenu, hash_password, verify_password,PrintMesg
from storage import delete_profile_transactions
def register():
    users = load_users()
    username = input('Enter a username ✎𓂃  ')
    if any(u["name"] == username for u in users):
        PrintMesg('Username already exists!')
        return None
    password = getpass.getpass('Enter a password ✎𓂃  ')
    
    user_id = str(uuid.uuid4())
    
    # Create default profile
    profile_name = input('Enter profile name ✎𓂃  ')
    if not profile_name.strip():
        PrintMesg('Profile name cannot be empty!')
        return
    
    currency = input('Enter currency (default is USD) ✎𓂃  ')
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
    PrintMesg('Registration successful!')
    PrintMesg(f'Created default profile "{profile_name}" with currency "{currency}".')
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
    username = input('Enter your username ✎𓂃  ')
    password = getpass.getpass('Enter your password ✎𓂃  ')
    for u in users:
       if u["name"] == username and verify_password(password, u["password"]):
           PrintMesg('Login successful!', 50)
           return username
    PrintMesg('Invalid username or password!')
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
        PrintMesg("Error: User data not found! Please login again.")
        return None
     
    while True:
        PrintMesg('Profile Management')
        
        userPrfiles = []
        
        for __, profile in enumerate(user_data["profiles"], 1):
            userPrfiles.append(f'{profile["profile_name"]} (Currency: {profile["currency"]})')
        userPrfiles.append('Create New Profile')
        userPrfiles.append('Delete Profile')
        userPrfiles.append('Logout')
        PrintMenu('Your Profiles',userPrfiles)
        choice = input('Select a profile number or option ✎𓂃  ')
        
        try:
            choice_num = int(choice)
            if 1 <= choice_num <= len(user_data["profiles"]):
                selected_profile = user_data["profiles"][choice_num - 1]
                PrintMesg(f'Switched to profile: {selected_profile["profile_name"]}')
                return selected_profile
            elif choice_num == len(user_data["profiles"]) + 1:
                create_new_profile(user)
                user_data = get_user_data(user)  # Refresh user data
            elif choice_num == len(user_data["profiles"]) + 2:
                delete_profile(user)
                user_data = get_user_data(user)  # Refresh user data
            elif choice_num == len(user_data["profiles"]) + 3:
                PrintMesg('Logging out...')
                return None
            else:
                PrintMesg('Invalid choice. Please try again.')
        except ValueError:
            PrintMesg('Invalid input. Please enter a number.')

def create_new_profile(user):
    """Create a new profile for the user"""
    users = load_users()
    
    profile_name = input('Enter profile name ✎𓂃  ')
    if not profile_name.strip():
        PrintMesg('Profile name cannot be empty!')
        return
    
    # Check for duplicate profile name
    user_data = get_user_data(user)
    if user_data and any(p['profile_name'] == profile_name for p in user_data.get('profiles', [])):
        PrintMesg(f'Profile "{profile_name}" already exists!')
        return
    
    currency = input('Enter currency (default is USD) ✎𓂃  ')
    if not currency.strip():
        currency = "USD"
    
    new_profile = create_profile_data(profile_name, currency)
    
    for u in users:
        if u["name"] == user:
            u["profiles"].append(new_profile)
            save_users(users)
            PrintMesg(f'Profile "{profile_name}" created successfully!')
            return
    
    PrintMesg('Error: User not found!')

def delete_profile(user):
    """Delete a profile"""
    user_data = get_user_data(user)
    
    if len(user_data["profiles"]) <= 1:
        PrintMesg('Cannot delete the last profile! You must have at least one profile.')
        return
    
    PrintMesg('Select profile to delete:')
    for idx, profile in enumerate(user_data["profiles"], 1):
        PrintMesg(f'{idx}. {profile["profile_name"]} (Currency: {profile["currency"]})')
    
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
                    PrintMesg(f'Profile "{profile_to_delete["profile_name"]}" deleted successfully!')
                    return
            PrintMesg('Authentication failed! Profile not deleted.')
        else:
            PrintMesg('Invalid choice.')
    except ValueError:
        PrintMesg('Invalid input. Please enter a number.')
