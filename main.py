from storage import monthly_backup
from users import register, login, profile_menu
from transactions import Transactions
from reports import Reports
from import_export import ImportExport
from recurring_transactions import execute_due_recurring_transactions
from utils import clear_screen, PrintMenu, PrintMesg

def menu():
    PrintMenu('Expense Tracker Main Menu', ['Login', 'Register', 'Exit'])
    return input('Please select an option ✎𓂃  ')


def HomePage(user, profile):
    while True:
        clear_screen()
        PrintMesg('Welcome to your Expense Tracker Home Page!',length= 76 ,printFotr=False)
        PrintMesg(f'User: {user} | Profile: {profile["profile_name"]} | Currency: {profile["currency"]}',length= 76 ,printHedr=False)
        PrintMenu('Home User Page Menu', ['Transactions', 'Reports', 'Import/Export', 'Switch Profile', 'Logout'])
        choice = input('Please select an option ✎𓂃  ')
        
        if choice == '1':
            Transactions(user, profile)
        elif choice == '2':
            Reports(user, profile)
        elif choice == '3':
            ImportExport(user, profile)
        elif choice == '4':
            new_profile = profile_menu(user)
            if new_profile:
                profile = new_profile
            else:
                return 'logout'
        elif choice == '5':
            print('Logging out...')
            return 'logout'
        else:
            print('Invalid choice. Please try again.')

if __name__ == '__main__':
    monthly_backup()
    execute_due_recurring_transactions()
    while True:
        clear_screen()
        choice = menu()
        if choice == '1':
            user = login()
            if user:
                while True:
                    profile = profile_menu(user)
                    if profile is None:
                        break
                    result = HomePage(user, profile)
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
