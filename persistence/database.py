"""
Persistence Layer — Database Module

This module handles database initialization and connection management. 
It uses SQLite, which is perfect for intermediate-level banking systems.

This layer is responsible for:
- Creating database schema
- Managing database connection
- Executing raw SQL queries
- Handling database connection
"""


import sqlite3
import os
from config.settings import APP_CONFIG


class Database:
    """
    Database class manages SQLite database operations.

    This class is a singleton-like pattern - there's typically only one
    database connection instance for the entire application.

    It handles:
    - Database file creation 
    - Schema setup (tables, indexes)
    - Connection management
    - SQL execution
    """


    def __init__(self):
        """
        Initialize the database connection and setup.

        This constructor:
        - sets the database path from configuration
        - initialize the database file (creates if doesn't exist)
        - sets up the schema (creates tables)
        """

        # Get database file path from configuration
        # This allows changing database location without code changes 
        self.db_path = APP_CONFIG['DATABASE_PATH']

        # Initialize the database (create file and schema)
        self._initialize_database()

    def _initialize_database(self):
        """
        Initialize the database by creating tables if they don't exist.

        This method:
        1. Creates tables for accounts and transactions
        2. Creates indexes for faster queries 
        3. Is safe to call multiple times (uses CREATE TABLE IF NOT EXISTS)
        """

        # Create a connection to the database 
        # sqlite3.connect() automatically creates the file if it doesn't exist 
        connection = sqlite3.connect(self.db_path)

        # Get a cursor to execute SQL commands 
        cursor = connection.cursor()

        try:
            # Creates ACCOUNTS table to store bank account information
            # This table structure follows normalization principles 
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    -- Primary Key: Unique identifier for each account 
                    account_number TEXT PRIMARY KEY, 

                    -- Name of the account holder 
                    holder_name TEXT NOT NULL,

                    -- Type of account: CHECKING OR SAVINGS 
                    account_type TEXT NOT NULL, 

                    -- Current balance in the account 
                    balance REAL NOT NULL, 

                    -- Status: ACTIVE, FROZEN, or CLOSED 
                    status TEXT NOT NULL,

                    -- When the account was created 
                    created_at TEXT NOT NULL,

                    -- When the last transaction occurred 
                    last_transaction_time TEXT
                )
            ''')

            # Create TRANSACTIONS table to store transaction history 
            # This is an append-only table for audit trail 
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    -- Primary Key: Unique identifier for each transaction
                    transaction_id TEXT PRIMARY KEY,

                    -- Accounts involved in this transaction
                    account_number TEXT NOT NULL,

                    -- Type of transaction
                    transaction_type TEXT NOT NULL,

                    -- Amount involved 
                    amount REAL NOT NULL,

                    -- Description or notes 
                    description TEXT,

                    -- Related account (for transfers)
                    related_account TEXT,

                    -- Balance after this transaction
                    balance_after REAL NOT NULL,

                    -- When the transaction occurred 
                    timestamp TEXT NOT NULL,

                    -- Status of the transaction
                    status TEXT NOT NULL,

                    -- Foreign key linking to accounts table 
                    FOREIGN KEY (account_number) REFERENCES accounts(account_number)
                )
            ''')

            # Create an index on account_number in transactions table 
            # Indexes speed up queries that filter by account_number 
            # Very important since we frequently look up transactions by account 

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transaction_account 
                    ON transactions(account_number)
            ''')

            # Create an index on timestamp for sorting queries 
            # Helpful when we need to find recent transactions 
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_transactions_timestamp
                    ON transactions(timestamp)
            ''')

            # Commit all the changes to the database 
            # Without commit, the changes are rolled back when connection closes 
            connection.commit()

            # Print confirmation that database was initialized
            print("[DATABASE] Database initialized successfully.")

        except sqlite3.Error as e:
            # If there's a database error, print it and rollback
            print(f"[ERROR] Database initialization error: {e}")
            connection.rollback()
            raise 

        finally:
            # Always close the connection when done 
            connection.close()

    def get_connection(self):
        """
        Get a database connection.

        This method returns a new connection to the database.
        Each connection should be closed after use.

        Returns:
            sqlite3.Connection: A database connection object 
        """

        # Create a new connection to the database 
        # The connection is not cached - each call creates a new one
        # This is a thread-safe and avoids connection state issues 
        connection = sqlite3.connect(self.db_path)

        # Enable foreign key constraints 
        # SQLite doesn't enforce foreign keys by default, this enable them 
        connection.execute('PRAGMA foreign_keys = ON')

        # Return the connection object
        return connection

    def execute_query(self, query, parameters=None):
        """
        Execute a SELECT query and return results.

        This method:
        1. Handles connection management (open and close)
        2. Execute the query safely with parameter binding
        3. Returns all results as a list 

        Args:
            query (str): SQL SELECT query with ? placeholders for parameters 
            parameters (tuple): Query parameters to bind (prevents SQL Injection)
        
        Returns:
            List: List of tuples, each tuple is a row
        """

        # Get a connection from the database 
        connection = self.get_connection()

        try:
            # Get a cursor from the connection
            cursor = connection.cursor()

            # Execute the query with parameters 
            # Using ? placeholders prevents SQL injection attacks 
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            # Fetch all results from query
            results = cursor.fetchcall()

            # Retun the list of rows 
            return results 

        finally:
            # Always close the connection to free resource
            connection.close()

    def execute_update(self, query, parameters=None):
        """
        Execute an INSERT, UPDATE, or DELETE query.

        Unlike SELECT queries, these modify the database.
        This method handles transactions properly.

        Args:
            Query (str): SQL query with ? placeholders.
            parameters (tuple): Query parameters to bind
        
        Returns:
            bool: True if successful, False otherwise
        """

        # Get a connection from the database 
        connection = self.get_connection()

        try:
            # Get a cursor from the connection
            cursor = connection.cursor()

            # Execute the query with parameters 
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)

            # Commit the transaction to make changes permanent
            connection.commit()

            # Return True to indicate success
            return True

        except sqlite3.Error as e:
            # If there's an error, rollback the transaction
            connection.rollback()

            # Print error message for debugging
            print(f"[ERROR] Database updater error: {e}")

            # Return false to indicate failure 
            return False

        finally:
            # Always close the connection
            connection.close()

    def execute_transaction(self, queries_and_params):
        """
        Execute multiple queries as a single transaction.

        A transaction ensures that either ALL queries succeed or NONE of them do.
        This is crucial for operations like transfers that involves multiple accounts.

        Args:
            queries_and_params (list): List of (queries, parameters) tuples.

        Returns:
            bool: True if all queries succeeded, False if any failed. 
        """

        # Get a connection from the database 
        connection = self.get_connection()

        try:
            # Get a cursor from the connection
            cursor = connection.cursor()

            # Execute each query in the transaction
            for query, params in queries_and_params:
                # Execute the query with parameters 
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

            # If all queries succeeded, commit the transaction
            connection.commit()

            # Return True to indicate all queries succeeded 
            return True 

        except sqlite3.Error as e:
            # If any queries fails, rollback all changes 
            # This maintains data consistency 
            connection.rollback()

            # Print error message 
            print(f'[ERROR] Transaction failed: {e}')

            # Return False to indicate transaction failed
            return False

        finally:
            # Always close the connection
            connection.close()

            