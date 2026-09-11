"""
Domain Layer — Account Model
============================
This module defines the core business object for a Bank Accocunt.
Domain models represent the real-world entities and contain business logic rules.
This layer is independent for any database or UI implementation.
"""

from datetime import datetime 
from config.settings import APP_CONFIG, ACCOUNT_STATUS, ACCOUNT_TYPES


class Account:
    """
    Account class represents a bank account in the real-world domain.

    This class encapsulates:
    - Account Data (account number, holder name, balance, etc)
    - Business Rules (minimum balance, overdraft protection, etc)
    - Account operations and state changes 
    
    This is a domain model, so it doesn't know about database or how it's persisted.
    """

    def __init__(self, account_number, holder_name, account_type, initial_balance=0):
        """
        Initialize a new account instance.

        Args:
            account_number (str): Unique identifier for the account
            holder_name (str): Name of the account holder
            account_type (str): Type of account (CHECKING or SAVINGS)
            initial_balance (float): Starting balance (Default: RM 0)
        """

        # Unique identifier for this account (e.g., ACC-001234)
        self.account_number = account_number 

        # Full name of the person who owns this account
        self.holder_name = holder_name

        # Type of account - CHECKING or SAVINGS
        self.account_type = account_type

        # Current balance of the account
        # This is the most important piece of account data 
        self.balance = initial_balance 

        # Status of the account - ACTIVE, FROZEN or CLOSED
        # New accounts are created in ACTIVE status (Default: ACTIVE)
        self.status = ACCOUNT_STATUS['ACTIVE']

        # Timestamp when the account was created
        # Used for audit trails and account history
        self.created_at = datetime.now()

        # Timestamp of the last transaction on this account
        # Helps track when the account was last used 
        self.transaction_time = None

        # Counter for number of transaction today
        # Used to enforce daily transaction limits
        self.daily_transaction_count = 0

        # Date when the daily transaction count was last reset 
        # Resets daily at midnight 
        self.daily_transaction_date = datetime.now().date()

    def deposit(self, amount):
        """
        Deposit money into the account.

        This method implements business logic for deposits:
        - Validate the amount is positive and within limits 
        - Updates the account balance 
        - Does NOT create a transaction record (that's done at persistence layer)
        
        Args:
            Amount (float): Amount to deposit (must be positive)
        
        Returns:
            Tuple: (success: bool, message: str)
                - (True, "success message") if deposit succeeds
                - (False, "error message") if deposit fails
        """

        # Validate that the account is in ACTIVE state
        # cannot deposit to frozen or closed accounts 
        if self.status != ACCOUNT_STATUS['ACTIVE']:
            return False, f"Cannot deposit to a {self.status} account"

        # Validate amount is a positive number 
        if amount <= 0:
            return False, "Deposit amount must be positive"

        # Validate amount doesn't exceed maximum allowed
        if amount > APP_CONFIG['MAX_TRANSACTION_AMOUNT']:
            return False, f"Deposit exceeds maximum amount of {APP_CONFIG['CURRENCY_SYMBOL']}{APP_CONFIG['MAX_TRANSACTION_AMOUNT']}"

        # Add the amount to the current balance 
        # This is the core operation that changes account state
        self.balance += amount

        # Record the time of the operation
        self.last_transaction_time = datetime.now()

        # Indicate success and provide confirmation message 
        return True, f"Deposited {APP_CONFIG['CURRENCY_SYMBOL']}{amount:.2f}. New Balance: {APP_CONFIG['CURRENCY_SYMBOL']}{self.balance:.2f}"

    def withdraw(self, amount):
        """
        Withdraw money from the account 

        This method implement business logic for withdrawals:
        - Validates the amount and account status
        - Checks if sufficient balance exists 
        - Updates the balance 
        - Applies overdraft penalty if necessary

        Args:
            amount (float): Amount to withdraw

        Returns:
            Tuple: (success: bool, message: str)
        """

        # Check if account is active (cannot withdraw from frozen/closed accounts)
        if self.status != ACCOUNT_STATUS['ACTIVE']:
            return False, f'Cannot withdraw from a {self.status} account'

        # Validate withdraw amount is positive 
        if amount <= 0:
            return False, f'Withdrawal amount must be positive'

        # Validate amount doesn't exceed transaction limit 
        if amount > APP_CONFIG['MAX_TRANSACTION_AMOUNT']:
            return False, f'Withdrawal exceeds maximum amount'

        # Check if account has sufficient balance for the withdrawal 
        if self.balance < amount:
            # Not enough funds - apply overdraft penalty
            penalty_amount = APP_CONFIG['OVERDRAFT_PENALTY']

            # Deduct the penalty from balance (to discourage overdrafts)
            self.balance -= penalty_amount

            # Record the time of this failed attempt 
            self.last_transaction_time = datetime.now()

            # Return failure with  explanation of what happened 
            return False, f"Insufficient funds. Available: {APP_CONFIG['CURRENCY_SYMBOL']}{self.balance + penalty_amount:.2f}. Overdraft Penalty ({APP_CONFIG['CURRENCY_SYMBOL']}{penalty_amount}) applied."


        # Sufficient balance exists, proceeds with withdrawal
        # Subtract the withdrawal amount from balance 

        self.balance -= amount 

        # Record the time of this operation 
        self.last_transaction_time = datetime.now()

        # Return success 
        return True, f"Withdrew {APP_CONFIG['CURRENCY_SYMBOL']}{amount:.2f}. New Balance: {APP_CONFIG['CURRENCY_SYMBOL']}{self.balance:.2f}"


    def get_balance(self):
        """
        Get the current balance of the account. 

        This is a simple getter that returns the current balance.
        Separating this as a method (rather than direct access) follows
        encapsulation principles — balance should only be modified through 
        withdrawal/deposit methods.
        
        returns:
            float: current account balance 
        """

        return self.balance 

    def check_daily_transaction_limit(self):
        """
        Check if the account has reached its daily limit transaction limit. 

        The system limits the number of transactions per day to prevent abuse. 
        This method checks if we've hit that limit. 

        Returns: 
            bool: Trus if limit is reached, False otherwise
        """

        # Check if we need to reset the daily counter (it's a new day)
        if datetime.now().date() > self.daily_transaction_date:
            # it's a new day, reset the counter 
            self.daily_transaction_count = 0
            self.daily_transaction_date = datetime.now().date()

        # Return true if we've hit the limit, false if we can still transact
        return self.daily_transaction_count >= APP_CONFIG['DAILY_TRANSACTION_LIMIT']

    def increment_daily_transaction_count(self):
        """
        Increment the transaction counter for today.

        Called after each successful transaction to track how many 
        transactions have occurred today.
        """

        # Increase the counter by 1
        self.daily_transaction_count += 1

    def freeze_account(self):
        """
        Freeze the account, preventing further transactions.

        This might be done for securify reasons or at customer request.
        A frozen account can still be viewed but not used.
        """

        # Change status to FROZEN
        self.status == ACCOUNT_STATUS['FROZEN']

    def unfreeze_account(self):
        """
        Unfreeze the account, allowing the transactions to resume.
        """

        # Change the status to ACTIVE
        self.status == ACCOUNT_STATUS['ACTIVE']

    def close_account(self):
        """
        Close the account permanently. 

        A closed account cannot be used and is marked as closed in the system.
        This is typically done when an account is no longer needed.
        """

        # Change status to CLOSED 
        self.status == ACCOUNT_STATUS['CLOSED']

    def __str__(self):
        """
        String representation of the account object.

        This is used when the account object is converted to string, 
        useful for displaying account information.
        
        Returns:
            str: Formatted account information
        """

        return f"Account({self.account_number}) - {self.holder_name} - Balance: {APP_CONFIG['CURRENCY_SYMBOL']}{self.balance:.2f} - status: {self.status}"

    

