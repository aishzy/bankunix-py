from datetime import datetime
from typing import Optional, List, Tuple
from models.domain_models import Account, AccountType, Transaction, TransactionType, TransactionStatus
from repositories.account_repository import AccountRepository
from repositories.transaction_repository import TransactionRepository
from utils.helpers import IDGenerator, ValidationUtils, CalculationUtils


class AccountServvice:
    """Service for account management"""

    def __init__(self):
        self.account_repo = AccountRepository()
        self.transaction_repo = TransactionRepository()

    def create_account(self, user_id: str, account_type: AccountType, currency: str = 'USD') -> Tuple[bool, str, Optional[Account]]:
        """
        Create a new account for user
        Returns: (success, message, account_object)
        """

        # Generate account details 
        account_id =  IDGenerator.generate_account_id()
        account_number = IDGenerator.generate_account_number()

        # Set interest rate based on account type
        interest_rates = {
            AccountType.CHECKING: 0.01,
            AccountType.SAVINGS: 0.05,
            AccountType.MONEY_MARKET: 0.03,
            AccountType.CERTIFICATE_OF_DEPOSIT: 0.04
        }

        account = Account (
            account_id = account_id, 
            user_id = user_id, 
            account_type = account_type,
            account_number = account_number,
            balance = 0.0,
            currency = currency,
            created_at = datetime.now(),
            interest_rates = interest_rates.get(account_type, 0.0)
        )

        if self.account_repo.create_account(account):
            return True, f'{account_type.value} Account created successfully', account
        else:
            return False, f'Error creating account', None
    
    def get_account(self, account_id: str) -> Optional[Account]:
        """Get account details"""
        return self.account_repo.get_account_by_id(account_id)
    
    def get_user_account(self, user_id: str) -> List[Account]:
        """Get all accounts for a user"""
        return self.account_repo.get_account_by_user(user_id)
    
    def depoosit(self, account_id: str, amount: float, description: str = 'Deposit') -> Tuple[bool, str]:
        """
        Deposit money to account
        Returns: (success, message)
        """

        # Validate amount 
        is_valid, msg = ValidationUtils.validate_amount(amount)
        if not is_valid:
            return False, msg
        
        account = self.account_repo.get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        if not account.is_active:
            return False, "Account is not active"
        
        # Update balance 
        new_balance = account.balance + amount
        if not self.account_repo.update_balance(account_id, new_balance):
            return False, "Error processing deposit"
        
        # Create transaction record 
        transaction = Transaction(
            transaction_id = IDGenerator.generate_transaction_id(),
            account_id = account_id,
            transactionType = TransactionType.DEPOSIT,
            amount = amount, 
            description = description,
            balance_after = new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = IDGenerator.reference_number()
        )

        if not self.account_repo.create_transaction(transaction):
            return False, "Error recording transaction"
        
        return True, f"Deposit of {amount} completed successfully."
    
    def withdraw(self, account_id: str, amount: float, description: str = 'withdrawal') -> Tuple[bool, str]:
        """
        withdraw money from account
        Returns: (success, message)
        """

        # Validate amount
        is_valid, msg = ValidationUtils.validate_amount(amount)
        if not is_valid:
            return False, msg
        
        account = self.account_repo.get_account_by_id(account_id)
        if not account: 
            return False, "Account not found"
        if not account.is_active:
            return False, "Account is not active"
        
        # Check sufficient balance
        if account.balance < amount:
            return False, f"Insufficient balance, Available: {account.balance}"
        
        # Update balance 
        new_balance = account.balance - amount
        if not self.account_repo.update_balance(account_id, new_balance):
            return False, "Error processing withdrawal"
        
        # Create transaction record
        transaction = Transaction (
            transaction_id = IDGenerator.generate_transaction_id(),
            account_id = account_id, 
            transaction_type = TransactionType.WITHDRAWAL,
            amount = amount, 
            description = description, 
            balance_after = new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = IDGenerator.generate_reference_number()
        )

        if not self.transaction_repo.create_transaction(transaction):
            return False, "Error recording transaction"
        
        return True, f"Withdrawal of {amount} completed successfully."
    
    def get_balance(self, account_id: str) -> Optional[float]:
        """Get current account balance"""
        account = self.account_repo.get_account_by_id(account_id)
        return account.balance if account else None
    
    def get_statement(self, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get account statement (transaction history)"""
        return self.transaction_repo.get_transaction_by_account(account_id, limit)
    
    def get_account_by_number(self, account_number: str) -> Optional[Account]:
        """Get account by account number"""
        return self.account_repo.get_account_by_number(account_number)
    
    def close_account(self, account_id: str) -> Tuple[bool, str]:
        """
        Close an account
        Returns: (success, message)
        """

        account = self.account_repo.get_account_by_id(account_id)
        if not account: 
            return False, "Account not found"
        
        # Check if balance is zero
        if account.balance > 0:
            return False, "Account must have zero balance to close"
        
        if self.account_repo.close_account(account_id):
            return True, "Account closed successfully."
        else:
            return False, "Error closing account"
        
    def apply_interest(self, account_id: str) -> Tuple[bool, str]:
        """
        Apply interest to account
        Returns: (success, message)
        """
        account = self.account_repo.get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        if not account.is_active or account.interest_rate == 0:
            return False, "Account not eligible for interest"
        
        # Calculate interest for one month 
        interest = CalculationUtils.calculate_simple_interest(account.balance, account.interest_rate, 12)
        interest = CalculationUtils.round_currency(interest)

        if interest <= 0:
            return True, "No interest accrued"
        
        # Add interest to account
        new_balance = account.balance + interest
        if not self.account_repo.update_balance(account_id, new_balance):
            return False, "Error applying interest"
    
        # Record interest transaction 
        transaction = Transaction (
            transaction_id = IDGenerator.generate_transaction_id(),
            account_id = account_id,
            transaction_type = TransactionType.INTEREST,
            amount = interest, 
            description = f'Interest accrual ({account.interest_rate}% APR)',
            balance_after = new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = IDGenerator.generate_reference_number()
        )

        if not self.transaction_repo.create_transaction(transaction):
            return False, "Error recording interest transaction"
        return True, f'Interest of {interest} applied successfully.'
    
    def get_total_balance(self, user_id: str) -> float:
        """Get total balance across all accounts"""
        return self.account_repo.get_total_balance_by_user(user_id)
    
    def apply_maintenance_fee(self, account_id: str) -> Tuple[bool, str]:
        """
        Apply accounts maintenance fee
        Returns: (success, message)
        """

        account = self.account_repo.get_account_by_id(account_id)
        if not account:
            return False, "Account not found"
        
        fee = CalculationUtils.calculate_account_fee(account.balance)

        if fee == 0:
            return True, "No maintenance fee applicable"
        
        if account.balance < fee:
            return False, "Insufficient balance for maintenance fee"
        
        new_balance = account.balance - fee
        if not self.account_repo.update_balance(account_id, new_balance):
            return False, "Error deducting fee"
        
        # Record fee transaction
        transaction = Transaction(
            transaction_id = IDGenerator.generate_account_id(),
            account_id = account_id, 
            transaction_type = TransactionType.FEE,
            amount = fee,
            description = "Monthly account maintenance fee",
            balance_after = new_balance, 
            timestamp = datetime.now(),
            status = TransactionStatus.COMPLETED,
            reference_number = IDGenerator.generate_reference_number()
        )

        if not self.transaction_repo.create_transaction(transaction):
            return False, "Error recording fee transaction"
        
        return True, f"Maintenance fee of {fee} deducted"