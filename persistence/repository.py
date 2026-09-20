"""
Persistence Layer — Repository Module 

This module implements the Repository pattern for data access.

The repository pattern:
- Abstracts database operations behind simple methods
- Separates data access from business logic.
- Makes it easy to test (can mock repository)
- Makes it easy to switch database (just change repository)

This layer works with domain objects and the database.
"""

from datetime import datetime
from domain.account import Account
from domain.transaction import Transaction
from persistence.database import Database 
from config.settings import ACCOUNT_STATUS, TRANSACTION_TYPES, APP_CONFIG


class AccountRepository:
    """
    AccountRepository handles all database operations for accounts.

    This repository:
    - Saves accounts to the database
    - Retrieves accounts from the database
    - Updates account information 
    - Converts between domain objects and database rows
    """

    def __init__(self):
        """
        Initialize the repository with a database connection.

        The repository uses dependency injection of the database.
        This makes it easy to test by providing a mock database.
        """

        # Create an instance of the Database class
        # The database handles all SQL operations

        self.db = Database()

    def save_account(self, account):
        """
        Save a new account to the database.

        This method converts to the domain object to database format
        and inserts it as a new row.

        Args:
            account (Account): Domain account object to save
        
        Returns:
            bool: True if save was successful, False otherwise
        """

        # SQL query to insert a new account record 
        # The ? placeholders prevents SQL injection

        query = '''
            INSERT INTO accounts 
            (account_number, holder_name, account_type, balance, status, created_at, last_transaction_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''

        # Prepare parameters from the account object
        # These values fill the ? placeholders in order

        parameters = (
            account.account_number,         # Account Number 
            account.holder_name,            # Holder name
            account.account_type,           # Account type (CHECKING or SAVINGS)
            account.balance,                # Initial balance
            account.status,                 # Status (ACTIVE)
            account.created_at.isoformat(), # Creation time as ISO string
            None                            # No transactions yet
        )


        # Execute the insert query 
        # Returns True if successful, False if failed
        return self.db.execute_update(query, parameters)

    def get_account_by_number(self, account_number):
        """
        Retrieve an account from the database by its account number.

        This is the most common operation - looking up an account.
        Converts database row back to domain Account object.

        Args:
            account_number(str): The account number to look up 
        
        Returns:
            Account: The account object, or None if not found
        """

        # SQL query to find an account by its number 
        query = '''
            SELECT account_number, holder_name, account_type, balance, status, created_at, last_transaction_time
            FROM accounts
            WHERE account_number = ?
        '''

        # Execute the query 
        results = self.db.execute_query(query, (account_number,))

        # Check if we found a result
        if not results:
            # No account found with this number 
            return None

        # Get the first (and only) result
        row = results[0]

        # Convert the database row back into an Account object 
        # Extract each field from the row tuple
        account = Account(
            account_number=row[0],      # Account Number
            holder_name=row[1],         # Holder name
            account_type=row[2],        # Account type 
            initial_balance=row[3]      # Current balance
        )

        # Set additional properties from the database 
        account.status = row[4]     # Status
        account.created_at = datetime.fromisoformat(row[5]) # Parse creation timestamp 

        # Parse last transaction time (could be None)
        if row[6]:
            account.last_transaction_time = datetime.fromisoformat(row[6])

        # Return the reconstructured account object 
        return account

    def get_all_accounts(self):
        """
        Retrieve all accounts from the database.

        This is useful for admin operations or generating reports.

        Returns:
            List: List of Account objects
        """

        # SQL query to get all accounts 
        query = '''
            SELECT account_number, holder_name, account_type, balance, status, created_at, last_transaction_time
            FROM accounts
            ORDER BY created_at DESC
        '''

        # Execute the query (no parameters needed)
        results = self.db.execute_query(query)

        # Convert each row to an Account object 
        accounts = []
        for row in results:
            # Create Account object for each row
            account = Account(
                account_number = row[0],
                holder_name = row[1],
                account_type = row[2],
                initial_balance = row[3]
            )

            account.status = row[4]
            account.created_at = datetime.fromisoformat(row[5])
            if row[6]:
                account.last_transaction_time = datetime.fromisoformat(row[6])

            # Add to list 
            accounts.append(account)

        # Return all accounts
        return accounts 

    def update_account(self, account):
        """
        Update an existing account in the database.
        
        After a transaction, the account balance and last transaction time
        need to be updated in the database.

        Args:
            account (Account): The account object with updated data
        
        Returns:
            bool: True if update successful
        """

        # SQL query to update an account
        # We update balance, status, and last transaction time

        query = '''
            UPDATE accounts 
            SET balance = ?, status = ?, last_transaction_time = ?
            WHERE account_number = ?
        '''

        # Prepare parameters
        parameters = (
            account.balance,            # Account balance
            account.status,             # Current status
            account.last_transaction_time.isoformat() if account.last_transaction_time else None,   # Last transaction time
            account.account_number      # Which account to update
        )

        # Execute the update
        return self.db.execute_update(query, parameters)


    class TransactionRepository:
        """
        TransactionRepository handles all database operations for transactions.

        This repository:
        - Records transactions in the database
        - Retrieves transaction history
        - Maintains an immutable audit trail 
        """

        def __init__(self):
            """
            Initialize the transaction repository.
            """

            # Create database instance 
            self.db = Database()

        def save_transaction(self, transaction):
            """
            Save a transaction to the database.

            Transactions are immutable - once created they cannot be changed. 
            This maintains integrity of the audit trail.
            
            Args:
                transaction (Transaction): the transaction to save

            Returns:
                bool: True if successful
            """

            # SQL query to insert a transaction
            query = '''
                INSERT INTO transactions
                (transaction_id, account_number, transaction_type, amount, description, 
                 related_account, balance_after, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''

            # Prepare parameters from transaction object
            parameters = (
                transaction.transaction_id, 
                transaction.account_number, 
                transaction.transaction_type, 
                transaction.amount,
                transaction.description,
                transaction.related_account,
                transaction.balance_after, 
                transaction.timestamp.isoformat(),
                transaction.status
            )

            # Execute the insert 
            return self.db.execute_update(query, parameters)

        def get_transactions_by_account(self, account_number, limit=50):
            """
            Get transaction history for an account.

            Returns the most recent transactions for an account.
            Useful for displaying account statements.
            
            Args:
                account_number (str): Account to get transactions for 
                limit (int): Maximum number of transactions to return 

            Returns:
                List: List of transaction object
            """

            # SQL query to get transactions
            # Orders by timestamp descending to show most recent first

            query = '''
                SELECT transaction_id, account_number, transaction_type, amount, description, 
                       related_account, balance_after, timestamp, status
                FROM transactions
                WHERE account_number = ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''

            # Execute the query 
            results = self.db.execute_query(query, (account_number, limit))

            # Convert rows to Transaction objects 
            transactions = []
            for row in results:
                # Create transaction object 
                transaction = Transaction(
                    account_number = row[1],
                    transaction_type = row[2],
                    amount = row[3],
                    description = row[4],
                    related_account = row[5],
                    balance_after = row[6]
                )

                # Set the ID and timestamp from database 
                transaction.transaction_id = row[0]
                transaction.timestamp = datetime.fromisoformat(row[7])
                transaction.status = row[8]

                # Add to list 
                transaction.append(transaction)

            # Return all transactions (most recent first)
            return transactions

        def get_account_statement(self, account_number, days=30):
            """
            Get account statement for a period.

            Used for generating reports of transactions over a date range. 

            Args:
                account_number (str): Account number
                days (int): How many days of history to include
            
            Returns:
                list: List of transactions
            """

            # SQL query with date filtering 
            # Calculate transactions within the last 'days' days
            query = '''
                SELECT transaction_id, account_number, transaction_type, amount, description,
                        related_account, balance_after, timestamp, status
                FROM transactions
                WHERE account_number = ?
                AND datetime(timestamp) >= datetime('now', ? || 'days')
                ORDER BY timestmap ASC
            '''

            # Execute with negative days value for "x days ago"
            results = self.db.execute_query(query, (account_number, -days))

            # Convert rows to Transactions object
            transactions = []
            for row in results:
                transaction = Transaction(
                    account_number = row[1],
                    transaction_type = row[2],
                    amount = row[3],
                    description = row[4],
                    related_Account = row[5],
                    balance_after = row[6]
                )

                transaction.transaction_id = row[0]
                transaction.timestamp = datetime.fromisoformat(row[7])
                transaction.status = row[8]

                transaction.append(transaction)

            return transactions
        


        






