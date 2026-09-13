"""
Domain Layer — Transaction Model

This module defines the Transaction domain object.
Transactions represent money movements in the banking system and maintain an audit trail.
"""


from datetime import datetime
from config.settings import TRANSACTION_TYPES, APP_CONFIG


class Transaction:
    """
    Transaction class represents a single banking transaction.

    Each transaction records:
    - Money movement (amount and type)
    - Source and destination accounts 
    - Timestamp for audit trail
    - Transaction status and description
    
    Transactions are immutable once created (append-only pattern) to maintain
    accurate audit trails and comply with banking regulations.
    """


    def __init__(self, account_number, transaction_type, amount, description="", related_account=None, balance_after=0):
        """
        Initialize a new transaction instance.

        Args:
            account_number (str): Account number involved in the transaction
            transaction_type (str): Type of transaction (DEPOSIT, WITHDRAWAL, TRANSFER, etc)
            amount (float): Transaction amount
            description (str): Optional description or notes about the transaction
            related_account (str): For transfers, other account involved 
            balance_after (float): Account balance after transaction
        """

        # Auto-generated ID for this transaction (timestamp-based)
        # Uses current time to create a unique transaction ID 
        # Format: TRANS-20240115143022 (date + time down to seconds)
        self.transaction_id = f"TRANS-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Account number this transaction belongs to
        self.account_number = account_number 

        # Type of transaction: DEPOSIT, WITHDRAWAL, TRANSFER, INTERNET, PENALTY
        self.transaction_type = transaction_type 

        # The amount of money involved in this transaction
        # Always stored as positive, type determines if it adds or subtracts from balance 
        self.amount = amount

        # Additional details about the transaction
        # E.g., "Transfer to John's account" or "Online Deposit"
        self.description = description 

        # For transfer transactions, this stores the related account number 
        # Helps track bilateral transfers
        self.related_account = related_account

        # The account balance immediately after this transaction 
        # Useful for reconciliation and history viewing 
        self.balance_after = balance_after 

        # Timestamp when the transaction occurred 
        # Accurate to microseconds for high-frequency systems 
        self.timestamp = datetime.now()

        # Status of the transaction: COMPLETED, PENDING, FAILED, REVERSED
        # New transaction start as COMPLETED (since we confirm before creating)
        self.status = 'COMPLETED'

    def get_display_amount(self):
        """
        Get the transaction amount with the appropriate sign for display. 

        In the banking systems, deposits show as + and withdrawals as -.
        this method returns the amount formatted for display.

        Returns:
            str: Formatted amount with sign and currency symbol
        """

        # Determine if this is a debit (money out) or credit (money in)
        is_credit = self.transaction_type in [
            TRANSACTION_TYPES['DEPOSIT'],
            TRANSACTION_TYPES['INTEREST']
        ]

        # Add + sign for credits, - sign for debits 
        sign = "+" if is_credit else "-"

        # Return formatted string with currency symbol 
        return f"{sign}{APP_CONFIG['CURRENCY_SYMBOL']}{self.amount:.2f}"

    def get_formatted_timestamp(self):
        """
        Get transaction timestamp in a human-readable format.

        Returns:
            str: Formatted timestamp string
        """

        return self.timestamp.strftime(APP_CONFIG['DATE_FORMAT'])

    def __str__(self):
        """
        String representation of the Transaction.

        Used when displaying transaction details to the user.
        Provides a summary of the transaction in one line.

        Returns:
            str: Formatted transaction summary
        """

        return (f"[{self.get_formatted_timestamp()}] {self.transaction_type}: " 
                f"{self.get_display_amount()} | Balance: {APP_CONFIG['CURRENCY_SYMBOL']}{self.balance_after:.2f} | " 
                f"Description: {self.description}")

    