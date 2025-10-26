from storage import monthly_backup
from users import register, login, profile_menu
from transactions import Transactions
from reports import Reports
from import_export import ImportExport


def menu():
    print('Welcome to the Expense Tracker!')
    print('1. Login')
    print('2. Register')
    print('3. Exit')
    return input('Please select an option: ')

def HomePage(user, profile):
    while True:
        print('\n' + '='*50)
        print('Welcome to your Expense Tracker Home Page!')
        print(f'User: {user} | Profile: {profile["profile_name"]} | Currency: {profile["currency"]}')
        print('='*50)
        print('1. Transactions')
        print('2. Reports')
        print('3. Import/Export')
        print('4. Switch Profile')
        print('5. Logout')
        print('='*50)
        choice = input('Please select an option: ')
        
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
    while True:
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
