import os
import sys
from datetime import datetime
from typing import Optional
from models.domain_models import User, AccountType
from services.auth_service import AuthenticationService
from services.account_service import AccountService
from services.transfer_bill_service import TransferService, BillPaymentService
from config.settings import get_config
from utils.helpers import FormatUtils


class BankingCLI:
    """Command Line Interface for Banking System"""

    def __init__(self):
        self.config = get_config()
        self.config.setup()

        self.auth_service = AuthenticationService()
        self.account_service = AccountService()
        self.transfer_service = TransferService()
        self.bill_service = BillPaymentService()

        self.current_user: Optional[User] = None
        self.current_account_id: Optional[str] = None

    def clear_screen(self):
        """Clear Screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_header(self, title: str = ''):
        """Display header"""
        self.clear_screen()
        print('=' * 70)
        print(f' {self.config.APP_NAME} v{self.config.APP_VERSION}')
        if title:
            print(f' {title}')
        print('=' * 70)
        print()

    def display_menu(self, options: dict, title: str = 'Menu'):
        """Display menu options"""
        print(f'\n{title}:')
        print('=' * 50)

        for key, value in options.items():
            print(f' {key}. {value}')
        print('=' * 50) 

    def get_input(self, prompt: str = 'Enter choice: ', strip: bool = True):
        """Get user input"""
        text = input(prompt)
        return text.strip() if strip else text
    
    def wait_for_continue(self):
        """Wait for user to continue"""
        input(f'\nPress ENTER to continue...')

    def print_success(self, message: str):
        """Print success message"""
        print(f"\n✓ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"\n✗ {message}")

"""
AUTHENTICATION FLOWS 
"""

def show_login_menu(self):
    """display login menu"""
    self.display_header("Welcome to BankUnix")
    print('\n1. Login')
    print('2. Register')
    print('3. Exit')

    choice = self.get_input('\nSelect Option:')

    if choice == '1':
        self.login()
    elif choice == '2':
        self.register()
    elif choice == '3':
        self.exit_app()
    else:
        self.print_error('Invalid options')
        self.wait_for_continue()
        self.show_login_menu()

def register(self):
    """Register new user"""
    self.display_header("Register New Account")

    full_name = self.get_input('Full Name: ')
    email = self.get_input('Email: ')
    phone = self.get_input('Phone: ')


    