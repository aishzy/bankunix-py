import sqlite3
from pathlib import Path
from typing import Optional
import threading


class DatabaseManager:
    """Manages SQLite database connections and initialization"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.db_path = Path(__file__).parent.parent / 'data' / 'banking.db'
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.connection = None
            self.initialized = True

    def get_connection(self) -> sqlite3.Connection:
        """Get or create database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute('PRAGMA foreign_keus = ON')
        return self.connection
    
    def initialize_database(self) -> None:
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.Cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAUlT 1,
                failed_login_attempts INTEGER DEFAULT 0,
                is_locked BOOLEAN DEFAULT 0,
                locked_until TIMESTAMP
            )        
        ''')

        # Accounts table 
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                account_type TEXT NOT NULL,
                account_number TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 0.0,
                currency TEXT DEFAULT 'MYR',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                last_transaction_at TIMESTAMP, 
                interest_rate REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Transaction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY, 
                account_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                balance_after REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'COMPLETED', 
                reference_number TEXT,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
        ''')

        # Transfers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transfers (
                transfer_id TEXT PRIMARY KEY,
                from_account_id TEXT NOT NULL,
                to_account_id TEXT NOT NULL,
                amount REAL NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
                completed_at TIMESTAMP,
                status TEXT DEFAULT 'PENDING',
                FOREIGN KEY (from account_id) REFERENCES accounts(account_id),
                FOREIGN KEY (to_account_id) REFERENCES accounts(account_id)
            )
        ''')

        # Bills table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                bill_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                biller_name TEXT NOT NULL,
                amount REAL NOT NULL,
                due_date DATE,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                FOREIGN KEY (account_id) REFERENCES accounts(account_id)
            )
        ''')

        # Audit log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                log_id TEXT PRIMARY KEY,
                user_id TEXT,
                action TEXT NOT NULL,
                resource_type TEXT,
                resource_id TEXT,
                changes TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                status TEXT DEFAULT 'SUCCESS',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')

        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_account_user ON accounts(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transaction_account ON transactions(account_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_transfer_accounts ON transfers(from account_id, to_account_id)')

        conn.commit()

        def close(self) -> None:
            """Close database connection"""
            if self.connection:
                self.connection.close()
                self.connection = None

        def __del__(self):
            self.close()