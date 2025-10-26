import uuid
import getpass
from storage import load_users, save_users, delete_profile_transactions
from utils import PrintMenu, hash_password, verify_password, PrintMesg ,clear_screen

def register():
    """Register a new user with validation"""
    users = load_users()
    
    # Username input with validation
    while True:
        username = input('Enter a username (3-20 characters) ✎𓂃: ').strip()
        
        if not username:
            PrintMesg('Username cannot be empty!')
            continue
            
        if len(username) < 3:
            PrintMesg('Username must be at least 3 characters long!')
            continue
            
        if len(username) > 20:
            PrintMesg('Username must be at most 20 characters long!')
            continue
            
        if not username.replace('_', '').replace('-', '').isalnum():
            PrintMesg('Username can only contain letters, numbers, hyphens and underscores!')
            continue
        
        if any(u["name"] == username for u in users):
            PrintMesg('Username already exists! Please choose another.')
            continue
        
        break
    
    # Password input with confirmation
    while True:
        password = getpass.getpass('\nEnter a password (minimum 6 characters): ')
        
        if len(password) < 6:
            print('\nPassword must be at least 6 characters long!')
            continue
        
        confirm_password = getpass.getpass('Confirm password: ')
        
        if password != confirm_password:
            print('\nPasswords do not match! Please try again.')
            continue
        
        break
    
    user_id = str(uuid.uuid4())
    
    # Create default profile
    while True:
        profile_name = input('\nEnter profile name ✎𓂃  : ').strip()
        if profile_name:
            break
        PrintMesg('Profile name cannot be empty!')
    
    currency = input('Enter currency (default is USD) ✎𓂃  ').strip().upper()
    if not currency:
        currency = "USD"
    
    default_profile = create_profile_data(profile_name, currency)
    
    user = {
        "user_id": user_id,
        "name": username,
        "password": hash_password(password),
        "profiles": [default_profile]
    }
    users.append(user)

    if save_users(users):
        clear_screen()
        PrintMesg('Registration successful!')
        PrintMesg(f'Created default profile "{profile_name}" with currency "{currency}".',length=75)
        input('\nPress Enter to continue...')
        return username
    else:
        PrintMesg('\nRegistration failed! Please try again.')
        input('\nPress Enter to continue...')
        return None


def create_profile_data(profile_name, currency):
    """Helper function to create profile data structure"""
    return {
        "profile_id": str(uuid.uuid4()),
        "profile_name": profile_name.strip(),
        "currency": currency.strip().upper()
    }


def login():
    """Login to existing account"""
    users = load_users()
    
    username = input('Enter your username ✎𓂃  ').strip()
    password = getpass.getpass('Enter your password ✎𓂃  ')
    
    for u in users:
        if u["name"] == username and verify_password(password, u["password"]):
            PrintMesg('Login successful!', 50)
            input('\nPress Enter to continue...')
            return username
    
    PrintMesg('Invalid username or password!')
    input('\nPress Enter to continue...')
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
    
    if not user_data:
        PrintMesg("Error: User data not found! Please login again.")
        input('\nPress Enter to continue...')
        return None
    
    while True:
        clear_screen()

        PrintMesg('Profile Management')
        
        userPrfiles = []
        
        for __, profile in enumerate(user_data["profiles"], 1):
            userPrfiles.append(f'{profile["profile_name"]} (Currency: {profile["currency"]})')
        userPrfiles.append('Create New Profile')
        userPrfiles.append('Delete Profile')
        userPrfiles.append('Logout')
        PrintMenu('Your Profiles',userPrfiles)
        choice = input('Select a profile number or option ✎𓂃  ').strip()
        
        try:
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(user_data["profiles"]):
                selected_profile = user_data["profiles"][choice_num - 1]
                PrintMesg(f'Switched to profile: {selected_profile["profile_name"]}')
                input('\nPress Enter to continue...')
                return selected_profile
                
            elif choice_num == len(user_data["profiles"]) + 1:
                create_new_profile(user)
                user_data = get_user_data(user)
                
            elif choice_num == len(user_data["profiles"]) + 2:
                delete_profile(user)
                user_data = get_user_data(user)
                
                # Check if user still has profiles
                if not user_data or not user_data.get("profiles"):
                    print('\nNo profiles remaining. Logging out...')
                    input('\nPress Enter to continue...')
                    return None
                    
            elif choice_num == len(user_data["profiles"]) + 3:
                PrintMesg('Logging out...')
                input('\nPress Enter to continue...')
                return None
                
            else:
                PrintMesg('Invalid choice. Please try again.')
                input('\nPress Enter to continue...')
                
        except ValueError:
            PrintMesg('Invalid input. Please enter a number.')
            input('\nPress Enter to continue...')


def create_new_profile(user):
    """Create a new profile for the user"""
    users = load_users()
    
    # Profile name input
    profile_name = input('Enter profile name ✎𓂃  ').strip()
    if not profile_name:
        PrintMesg('Profile name cannot be empty!')
        input('\nPress Enter to continue...')
        return
    
    # Check for duplicate profile name
    user_data = get_user_data(user)
    if user_data:
        existing_names = [p['profile_name'].lower() for p in user_data.get('profiles', [])]
        if profile_name.lower() in existing_names:
            PrintMesg(f'Profile "{profile_name}" already exists!')
            input('\nPress Enter to continue...')
            return
    
    # Currency input
    currency = input('Enter currency (default is USD) ✎𓂃  ').strip().upper()
    if not currency:
        currency = "USD"
    
    new_profile = create_profile_data(profile_name, currency)
    
    # Add profile to user
    for u in users:
        if u["name"] == user:
            u["profiles"].append(new_profile)
            if save_users(users):
                 PrintMesg(f'Profile "{profile_name}" created successfully!')
            else:
                print('\nFailed to create profile!')
            input('\nPress Enter to continue...')
            return
    
    PrintMesg('Error: User not found!')
    input('\nPress Enter to continue...')


def delete_profile(user):
    """Delete a profile with confirmation"""
    user_data = get_user_data(user)
    
    if not user_data:
        print('\nError: User not found!')
        input('\nPress Enter to continue...')
        return
    
    if len(user_data["profiles"]) <= 1:
        PrintMesg('Cannot delete the last profile! You must have at least one profile.')
        input('\nPress Enter to continue...')
        return
    
    print('\n' + '='*50)
    PrintMesg('Select profile to delete:')
    print('='*50)
    for idx, profile in enumerate(user_data["profiles"], 1):
        PrintMesg(f'{idx}. {profile["profile_name"]} (Currency: {profile["currency"]})')
    print('='*50)
    
    choice = input('\nEnter profile number to delete (or 0 to cancel): ').strip()
    
    try:
        choice_num = int(choice)
        
        if choice_num == 0:
            print('\nDeletion cancelled.')
            input('\nPress Enter to continue...')
            return
            
        if 1 <= choice_num <= len(user_data["profiles"]):
            profile_to_delete = user_data["profiles"][choice_num - 1]
            
            # Confirm deletion
            print(f'\nWarning: This will delete profile "{profile_to_delete["profile_name"]}" and ALL its transactions!')
            confirm = input('Type "DELETE" to confirm: ').strip()
            
            if confirm != "DELETE":
                print('\nDeletion cancelled.')
                input('\nPress Enter to continue...')
                return
            
            # Verify password
            password = getpass.getpass('\nEnter your password to confirm: ')
            users = load_users()
            
            for u in users:
                if u["name"] == user and verify_password(password, u["password"]):
                    profile_id = profile_to_delete["profile_id"]
                    
                    # Delete associated transactions
                    print('\nDeleting transactions...')
                    delete_profile_transactions(profile_id)
                    
                    # Remove profile
                    del u["profiles"][choice_num - 1]
                    
                    if save_users(users):
                        PrintMesg(f'Profile "{profile_to_delete["profile_name"]}" deleted successfully!')
                    else:
                        print('\nFailed to delete profile!')
                    
                    input('\nPress Enter to continue...')
                    return
            
            PrintMesg('Authentication failed! Profile not deleted.')
            input('\nPress Enter to continue...')
        else:
            PrintMesg('Invalid choice.')
            input('\nPress Enter to continue...')
            
    except ValueError:
        PrintMesg('Invalid input. Please enter a number.')
        input('\nPress Enter to continue...')
