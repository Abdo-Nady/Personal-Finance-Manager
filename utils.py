import datetime
import os
import bcrypt


def hash_password(password):
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed_password):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def format_currency(amount, currency):
    return f"{amount:.2f} {currency}"

def validate_date(date_str):
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False



def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')
  

def PrintMenu(name: str ,options: list[str]):
    name = name if len(name) % 2 == 0 else name + ' '
    print('╔' + '═'*50 + '╗')
    print('╟'+ ('─'* (25 - int(len(name)/2))) + name +('─'* (25 - int(len(name)/2)))+'╢')
    print('╠═══╦' + '═'*46 + '╣')
    for i in range(0, len(options)):
        print(f'║ {i+1} ║'+(' ' + options[i]+ ' '*60)[:46]+ '║')
        if(i < len(options)-1): print('╠═══╬' + '═'*46 + '╣')
    print('╚═══╩' + '═'*46 + '╝')


def PrintMesg(mesg: str, length: int = 50, printHedr: bool = True, printFotr: bool = True):
    mesg = mesg if len(mesg) % 2 == 0 else mesg + ' '
    if(printHedr): print('╔' + '═'*length + '╗')
    print('╟'+ ('─'* (int(length/2) - int(len(mesg)/2))) + mesg +('─'* (int(length/2) - int(len(mesg)/2)))+'╢')
    if(printFotr): print('╚' + '═'*length + '╝')