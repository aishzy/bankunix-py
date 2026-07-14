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
    
    
    print("\nPassword must contain:")
    print("  • At least 8 characters")
    print("  • Uppercase and lowercase letters")
    print("  • Numbers and special characters")
    
    password = self.get_input("Password: ", strip=False)
    confirm_password = self.get_input("Confirm Password: ", strip=False)

    if password != confirm_password:
        self.print_error("Password do not match")
        self.wait_for_continue()
        return
    
    success, message, user = self.auth_service.register_user(
        full_name, email, phone, password
    )

    if success:
        self.print_success(message)
        self.wait_for_continue()
        self.show_login_menu()
    else:
        self.print_error(message)
        self.wait_for_continue()

    def login(self):
        """Login user"""    
        self.display_header('Login')

        email = self.get_input('Email: ')
        password = self.get_input('Password: ', strip=False)

        success, message, user = self.auth_service.login(email, password)

        if success:
            self.current_user = user
            self.print_success(message)
            self.wait_for_continue()
            self.show_dashboard()
        else:
            self.print_error(message)
            self.wait_for_continue()
            self.show_login_menu()

    # MAIN DASHBOARD 
    def show_dashboard(self):
        """Show main dashboard"""
        while True:
            self.display_header(f'Dashboard - {self.current_user.full_name}')

            accounts = self.account_service.get_user_accounts(self.current_user.user_id)
            total_balance = self.account_service.get_total_balance(self.current_user.user_id)

            print(f'\nWelcome Back, {self.current_user.full_name}')
            print(f'Total Balance: {FormatUtils.format_currency(total_balance)}')
            print(f'\nAccounts ({len(accounts)}):')

            if accounts:
                for idx, account in enumerate(accounts, 1):
                    print(f' {idx}. {account.get_account_type_display()}')
                    print(f' Account: {FormatUtils.mask_account_number(account.account_number)}')
                    print(f' Balance: {FormatUtils.format_currency(account.balance)}')
            else:
                print('No Accounts Found')

            options = {
                '1': 'View Account',
                '2': 'Create Account',
                '3': 'Transfer Money',
                '4': 'Pay Bills',
                '5': 'Settings',
                '6': 'Logout'
            }

            self.display_menu(options)
            choice = self.get_input()

            if choice == '1':
                self.view_account_menu()
            elif choice == '2':
                self.create_account()
            elif choice == '3':
                self.transfer_menu()
            elif choice == '4':
                self.bills_menu()
            elif choice == '5':
                self.settings_menu()
            elif choice == '6':
                self.logout()
                break
            else:
                self.print_error('Invalid Options')
                self.wait_for_continue()

    # Account Operations

    def view_account_menu(self):
        """Show account selection menu"""
        self.display_header('Select Account')

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        if not accounts:
            self.print_error('No Accounts found')
            self.wait_for_continue()
            return
        
        for idx, account in enumerate(accounts, 1):
            print(f'{idx}, {account.get_account_type_display()} - {FormatUtils.format_currency(account.balance)}')

        choice = self.get_input('\nSelect Account: ')
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                self.current_account_id = accounts[idx].account_id
                self.view_account_details()
            else:
                self.print_error('Invalid Selection')
                self.wait_for_continue()
        except ValueError:
            self.print_error("Invalid Input")
            self.wait_for_continue()
    
    def view_account_details(self):
        """Display account details and options"""
        while True:
            account = self.account_service.get_account(self.current_account_id)
            if not account:
                self.print_error("Account not found")
                return
            
            print(f'Account Number: {FormatUtils.mask_account_number(account.account_number)}')
            print(f'Balance: {FormatUtils.format_currency(account.balance)}')
            print(f'Currency: {account.currency}')
            print(f'Created: {FormatUtils.format_date(account.created_at)}')
            print(f'Interest Rate: {account.interest_rate}% APR')

            options = {
                "1": "Deposit",
                "2": "Withdraw",
                "3": "View Statement",
                "4": "Close Account",
                "5": "Back"
            }

            self.display_menu(options)
            choice = self.get_input()

            if choice == "1":
                self.deposit()
            elif choice == "2":
                self.withdraw()
            elif choice == "3":
                self.view_statement()
            elif choice == "4":
                self.close_account()
            elif choice == "5":
                break
            else:
                self.print_error("Invalid option")
                self.wait_for_continue()

                