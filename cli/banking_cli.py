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
        """Clear screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title: str = ""):
        """Display header"""
        self.clear_screen()
        print("=" * 70)
        print(f"  {self.config.APP_NAME} v{self.config.APP_VERSION}")

        if title:
            print(f"    {title}")
        print("=" * 70)
        print()
    
    def display_menu(self, options: dict, title: str = "Menu"):
        """Display menu options"""
        print(f"\n{title}")
        print("-" * 50)
        for key, value in options.items():
            print(f"   {key}. {value}")
        print("-" * 50)

    def get_input(self, prompt: str = "Enter choice: ", strip: bool = True):
        """Get user input"""
        text = input(prompt)
        return text.strip() if strip else text

    def wait_for_continue(self):
        """Wait for user to continue"""
        input("\nPress ENTER to continue...")

    def print_success(self, message: str):
        """Print success message"""
        print(f"\n✓ {message}")
    
    def print_error(self, message: str):
        """Print error message"""
        print(f"\n✗ {message}")
    
    # AUTHENTICATION FLOWS 

    def show_login_menu(self):
        """Display login menu"""
        self.display_header("Welcome to BankUnix")
        print("\n1. Login")
        print("2. Register")
        print("3. Exit")

        choice = self.get_input("\nSelect Option: ")

        if choice == "1":
            self.login()
        elif choice == "2":
            self.register()
        elif choice == "3":
            self.exit_app()
        else:
            self.print_error("Invalid option")
            self.wait_for_continue()
            self.show_login_menu()

    def register(self):
        """Register new user"""
        self.display_header("Register new Account")

        full_name = self.get_input("Full Name: ")
        email = self.get_input("Email: ")
        phone = self.get_input("Phone: ")

        
        print("\nPassword must contain:")
        print("  • At least 8 characters")
        print("  • Uppercase and lowercase letters")
        print("  • Numbers and special characters")

        password = self.get_input("Password: ", strip=False)
        confirm_password = self.get_input("Confirm Password: ", strip=False)

        if password != confirm_password:
            self.print_error("Password don't match")
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
        """Login User"""
        self.display_header("Login")

        email = self.get_input("Email: ")
        password = self.get_input("Password: ", strip=False)

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
            self.display_header(f"Dashboard - {self.current_user.full_name}")

            accounts = self.account_service.get_user_accounts(self.current_user.user_id)
            total_balance = self.account_service.get_total_balance(self.current_user.user_id)


            print(f"\nWelcome back, {self.current_user.full_name}")
            print(f"Total Balance: {FormatUtils.format_currency(total_balance)}")
            print(f"\nAccounts ({len(accounts)}):")

            if accounts:
                for idx, account in enumerate(accounts, 1):
                    print(f"   {idx}. {account.get_account_type_display()}")
                    print(f"      Account: {FormatUtils.mask_account_number(account.account_number)}")
                    print(f"      Balance: {FormatUtils.format_currency(account.balance)}")
            else:
                print(" No Account found")

            options = {
                "1": "View Account",
                "2": "Create Account",
                "3": "Transfer Money",
                "4": "Pay Bills",
                "5": "Settings",
                "6": "Logout"
            }

            self.display_menu(options)
            choice = self.get_input()

            if choice == "1":
                self.view_account_menu()
            elif choice == "2":
                self.create_account()
            elif choice == "3":
                self.transfer_menu()
            elif choice == "4":
                self.bills_menu()
            elif choice == "5":
                self.settings_menu()
            elif choice == "6":
                self.logout()
                break
            else:
                self.print_error("Invalid Option")
                self.wait_for_continue()

    # ACCOUNT OPERATIONS

    def view_account_menu(self):
        """Show account selection menu"""
        self.display_header("Select Account")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        if not accounts:
            self.print_error("No Accounts found")
            self.wait_for_continue()
            return

        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()} - {FormatUtils.format_currency(account.balance)}")

        choice = self.get_input("\nSelect Account: ")

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                self.current_account_id = accounts[idx].account_id
                self.view_account_details()
            else:
                self.print_error("Invalid selection")
                self.wait_for_continue()
        except ValueError:
            self.print_error("Invalid input")
            self.wait_for_continue()

    def view_account_details(self):
        """Display account details and options"""
        while True:
            account = self.account_service.get_account(self.current_account_id)
            if not account:
                self.print_error("Account not found")
                return

            self.display_header(f"{account.get_account_type_display()} Details")

            print(f"Account Number: {FormatUtils.mask_account_number(account.account_number)}")
            print(f"Balance: {FormatUtils.format_currency(account.balance)}")
            print(f"Currency: {account.currency}")
            print(f"Created: {FormatUtils.format_date(account.created_at)}")
            print(f"Interest Rate: {account.interest_rate}% APR")

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

    def create_account(self):
        """Create new account"""
        self.display_header("Create New Account")

        print("Select account type:")
        for idx, at in enumerate(AccountType, 1):
            print(f"   {idx}. {at.value}")

        choice = self.get_input("\nSelect type: ")

        try:
            idx = int(choice) - 1
            account_types = list(AccountType)
            if 0 <= idx < len(account_types):
                account_type = account_types[idx]
                success, message, account = self.account_service.create_account(
                    self.current_user.user_id, account_type
                )

                if success:
                    self.print_success(message)
                    print(f"Account Number: {account.account_number}")
                else:
                    self.print_error(message)
            else:
                self.print_error("Invalid selection")
        except ValueError:
            self.print_error("Invalid input")

        self.wait_for_continue()

    def withdraw(self):
        """Withdraw money"""
        self.display_header("Withdraw Money")

        try:
            amount = float(self.get_input("Enter amount: "))
            description = self.get_input("Description (optional): ") or "withdrawal"

            success, message = self.account_service.withdraw(
                self.current_account_id, amount, description
            )

            if success:
                self.print_success(message)
                account = self.account_service.get_account(self.current_account_id)
                print(f"New Balance: {FormatUtils.format_currency(account.balance)}")
            else:
                self.print_error(message)
        except ValueError:
            self.print_error("Invalid amount")

        self.wait_for_continue()

    def view_statement(self):
        """View account statement"""
        self.display_header("Account Statement")

        transactions = self.account_service.get_statement(self.current_account_id, limit=20)

        if not transactions:
            print("No transactions found")
        else:
            print(f"{'date':<20} {'type':<15} {'amount':<12} {'balance':<12}")
            print("-" * 60)

            for txn in transactions:
                print(f"{FormatUtils.format_datetime(txn.timestamp):<20} "
                      f"{txn.transaction_type.value:<15} "
                      f"{FormatUtils.format_currency(txn.amount):<12} "
                      f"{FormatUtils.format_currency(txn.balance_after):<12}")
        
        self.wait_for_continue()

    def close_account(self):
        """Close account"""
        self.display_header("Close Account")

        account = self.account_service.get_account(self.current_account_id)
        print(f"Account: {account.get_account_type_display()}")
        print(f"Balance: {FormatUtils.format_currency(account.balance)}")

        if account.balance > 0:
            self.print_error("Account must have zero balance to close")
            self.wait_for_continue()
            return

        confirm = self.get_input("\nAre you sure? (yes/no): ").lower()

        if confirm == "yes":
            success, message = self.account_service.close_account(self.current_account_id)

            if success: 
                self.print_success(message)
                self.current_account_id = None
            else:
                self.print_error(message)

        self.wait_for_continue()

    # TRANSFER MENU 

    def transfer_menu(self):
        """Show transfer menu"""
        self.display_header("Transfer Menu")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        if len(accounts) < 2:
            self.print_error("You need at least 2 accounts to transfer money")
            self.wait_for_continue()
            return

        options = {
            "1": "Transfer between my accounts",
            "2": "View Transfer History",
            "3": "Back"
        }

        self.display_header(options)
        choice = self.get_input()

        if choice == "1":
            self.transfer_internal()
        elif choice == "2":
            self.view_transfers()
        elif choice != "3":
            self.print_error("Invalid option")
            self.wait_for_continue()

    def transfer_internal(self):
        """Transfer between own accounts"""
        self.display_header("Transfers Between Accounts")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        print("From Account:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()} - {FormatUtils.format_currency(account.balance)}")

        from_choice = self.get_input("\nSelect from account: ")

        try:
            from_idx = int(from_choice) - 1
            if not (0 <= from_idx < len(accounts)):
                self.print_error("Invalid selection")
                return

            print("\nTo Account:")
            for idx, account in enumerate(accounts, 1):
                if idx != from_idx + 1:
                    print(f"{idx}. {account.get_account_type_display()}")

            to_choice = self.get_input("\nSelect to account: ")
            to_idx = int(to_choice) - 1

            if not (0 <= to_idx < len(accounts)) or from_idx == to_idx:
                self.print_error("Invalid selection")
                return

            amount = float(self.get_input("Amount: "))
            description = self.get_input("Description: ") or "Transfer"

            success, message = self.transfer_service.tranfer_money(
                accounts[from_idx].account_id,
                accounts[to_idx].account_id,
                amount, 
                description
            )

            if success:
                self.print_success(message)
            else:
                self.print_error(message)
        except (ValueError, IndexError):
            self.print_error("Invalid input")

        self.wait_for_continue()

    def view_transfers(self):
        """View transfer history"""
        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        if not accounts:
            print("No accounts")
            return

        self.display_header("Transfer History")

        print("Select Account:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()}")

        choice = self.get_input("\nSelect: ")

        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                transfers = self.transfer_service.get_transfer_history(accounts[idx].account_id)

                if not transfers:
                    print("No Transfers found")
                else:
                    for transfer in transfers:
                        print(f"\n{transfer.transfer_id}")
                        print(f"   Amount: {FormatUtils.format_currency(transfer.amount)}")
                        print(f"   Status: {transfer.status.value}")
                        print(f"   Date: {FormatUtils.format_datetime(transfer.created_at)}")
        except ValueError:
            self.print_error("Invalid input")

        self.wait_for_continue()


    # BILLS MENU 
     
    def bills_menu(self):
        """Show bills menu"""
        self.display_header("Bills Payment")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        if not accounts:
            self.print_error("No accounts found")
            self.wait_for_continue()
            return

        options = {
            "1": "Add Bill",
            "2": "Pay Bill", 
            "3": "View Bills", 
            "4": "Back"
        }

        self.display_menu(options)
        choice = self.get_input()

        if choice == "1":
            self.add_bill()
        elif choice == "2":
            self.pay_bill()
        elif choice == "3":
            self.view_bills()
        elif choice != "4":
            self.print_error("Invalid option")
            self.wait_for_continue()

    def add_bill(self):
        """Add new bill"""
        self.display_header("Add Bill")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        print("Select Account:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()}")

        try:
            account_choice = int(self.get_input("\nSelect account: ")) - 1
            if not (0 <= account_choice < len(accounts)):
                self.print_error("Invalid selection")
                return

            biller = self.get_input("Biller Name: ")
            amount = float(self.get_input("Amount: "))
            due_date_str = self.get_input("Due Date (DD-MM-YYYY): ")
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")

            success , message = self.bill_service.add_bill(
                accounts[account_choice].account_id,
                biller,
                amount, 
                due_date
            )

            if success:
                self.print_success(message)
            else:
                self.print_error(message)
        except (ValueError, IndexError):
            self.print_error("Invalid input")


    def pay_bill(self):
        """Pay a bill"""
        self.display_header("Pay Bill")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        print("Select Account:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()}")

        try:
            account_choice = int(self.get_input("\nSelect Account: ")) - 1
            if not (0 <= account_choice < len(accounts)):
                return

            bills = self.bill_service.get_pending_bills(accounts[account_choice].account_id)

            if not bills:
                print("No Pending Bills")
                self.wait_for_continue()
                return

            print("\nPending Bills:")
            for idx, bill in enumerate(bills, 1):
                print(f"{idx}. {bill.biller_name} - {FormatUtils.format_currency(bill.amount)}")

                bill_choice = int(self.get_input("\nSelect Bill: ")) - 1
                if 0 <= bill_choice < len(bills):
                    success, message = self.bill_service.pay_bill(bills[bill_choice].bill_id)

                    if success:
                        self.print_success(message)
                    else:
                        self.print_error(message)
        except ValueError:
            self.print_error("Invalid input")

        self.wait_for_continue()

    def view_bills(self):
        """View bills"""
        self.display_header("View Bills")

        accounts = self.account_service.get_user_accounts(self.current_user.user_id)

        print("Select Account:")
        for idx, account in enumerate(accounts, 1):
            print(f"{idx}. {account.get_account_type_display()}")

        try:
            choice = int(self.get_input("\nSelect: ")) - 1
            if 0 <= choice < len(accounts):
                bills = self.bill_service.get_bill_history(accounts[choice].account_id)

                if not bills:
                    print("No bills")
                else:
                    for bill in bills:
                        print(f"\n{bill.biller_name}")
                        print(f"   Amount: {FormatUtils.format_currency(bill.amount)}")
                        print(f"   Due: {FormatUtils.format_date(bill.due_date)}")
                        print(f"   Status: {bill.status.value}")
        except ValueError:
            self.print_error("Invalid input")

        self.wait_For_continue()


    # SETTINGS
    def settings_menu(self):
        """Show settings menu"""
        self.display_header("Settings")

        options = {
            "1": "Change Password", 
            "2": "View Profile", 
            "3": "Back"
        }

        self.display_menu(options)
        choice = self.get_input()

        if choice == "1":
            self.change_password()
        elif choice == "2":
            self.view_profile()
        elif choice != "3":
            self.print_error("Invalid option")
            self.wait_for_continue()

    def change_password(self):
        """Change password"""
        self.display_header("Change password")

        old_password = self.get_input("Current Password: ", strip=False)
        new_password = self.get_input("New Password: ", strip=False)
        confirm_password = self.get_input("Confirm Password: ", strip=False)

        if new_password != confirm_password:
            self.print_error("Password don't match")
        else:
            success, message = self.auth_service.change_password (
                self.current_user.user_id, old_password, new_password
            )

            if success:
                self.print_success(message)
            else:
                self.print_error(message)
        self.wait_for_continue()

    def view_profile(self):
        """View user profile"""
        self.display_header("User Profile")

        profile = self.auth_service.get_user_profile(self.current_user.user_id)

        if profile:
            print(f"Name: {profile['full_name']}")
            print(f"Email: {FormatUtils.mask_email(profile['email'])}")
            print(f"Phone: {profile['phone']}")
            print(f"Member Since: {FormatUtils.format_date(profile['created_at'])}")
            print(f"Status: {'Active' if profile['is_active'] else 'Inactive'}")

        self.wait_for_continue()

    # LOGOUT

    def logout(self):
        """Logout user"""
        self.current_user: None
        self.current_account_id: None
        self.print_success("Logged out successfully")
        self.wait_for_continue()

    def exit_app(self):
        """Exit application"""
        print("\nThank you for using BankUnix. Goodbye!")
        sys.exit(0)

    def run(self):
        """Run the Banking Application"""
        try:
            while True:
                if not self.current_user:
                    self.show_login_menu()
        except KeyboardInterrupt:
            print("\n\nApplication Interrupted")
            sys.exit(0)
        except Exception as e:
            print(f"\n✗ An error occurred: {str(e)}")
            sys.exit(1)