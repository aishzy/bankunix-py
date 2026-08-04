from datetime import datetime
from typing import Optional, List
import sqlite3
from models.domain_models import Transaction, TransactionType, TransactionStatus
from database.db_connection import DatabaseManager


class TransactionRepository:
    """Repository for transaction data access"""

    def __init__(self):
        self.db_manager = DatabaseManager()

    def create_transaction(self, transaction: Transaction) -> bool:
        """Create a new transaction"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO transactions (transaction_id, account_id, transaction_type, amount, 
                                          description, balance_after, timestamp, status, reference_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.account_id, transaction.transaction_type, transaction.amount, transaction.description,
                  transaction.balance_after, transaction.timestamp, transaction.status.value, transaction.reference_number))
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_transactions_by_id(self, transaction_id: str) -> Optional[Transaction]:
        """Retrieve transaction by ID"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
        row = cursor.fetchone()
        return self._map_to_transaction(row) if row else None

    def get_transactions_by_account(self, account_id: str, limit: int = 100) -> List[Transaction]:
        """Get transactions for an account (most recent first)"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions
            WHERE account_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (account_id, limit))
        rows = cursor.fetchcall()
        return [self._map_to_transaction(row) for row in rows]

    def get_transactions_in_date_range(self, account_id: str, start_date: datetime, end_date: datetime) -> List[Transaction]:
        """Get transaction within a date range"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM transactions
            WHERE account_id = ? AND timestamp BETWEEN ? AND ? 
            ORDER BY timestamp DESC
        ''', (account_id, start_date, end_date))
        rows = cursor.fetchcall()
        return [self._map_to_transaction(row) for row in rows]

    def get_daily_transaction(self, account_id: str, date: datetime) -> List[Transaction]:
        """Get transactions for a specific day"""
        start = datetime(date.year, date.month, date.day, 0, 0, 0)
        end = datetime(date.year, date.month, date.day, 23, 59, 59)
        return self.get_transactions_in_date_range(account_id, start, end)

    def update_transaction_status(self, transaction_id: str, status: TransactionStatus) -> bool:
        """Update transaction status"""
        try:
            conn = self.db_manager.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE transactions
                SET status = ? 
                WHERE transaction_id = ?
            ''', (status.value, transaction_id))
            conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_account_statement(self, account_id: str, limit: int = 50) -> List[Transaction]:
        """Get account statement (recent transactions)"""
        return self.get_transactions_by_account(account_id, limit)

    def get_total_transactions_count(self, account_id: str) -> int:
        """Get total number of transactions for an account"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) as count FROM transactions WHERE account_id = ?', (account_id,))
        row = cursor.fetchone()
        return row['count']

    def get_monthly_transaction_summary(self, account_id: str, year: int, month: int) -> dict:
        """Get transaction summary for a month"""
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT
                transaction_type,
                COUNT(*) as count,
                SUM(amount) as total,
            FROM transactions
            WHERE account_id = ?
                AND strftime('%Y', timestamp) = ?
                AND strftime('%m', timestamp) = ?
            GROUP BY transaction_type
        ''', (account_id, str(year).zfill(4), str(month).zfill(2)))

        rows = cursor.fetchcall()
        summary = {}
        for row in rows:
            summary[row['transaction_type']] = {
                'count': row['count'],
                'total': row['total']
            }
        return summary

    @staticmethod
    def _map_to_transaction(row: sqlite3.Row) -> Transaction:
        """Map database to transaction object"""
        return Transaction(
            transaction_id = row['transaction_id'],
            account_id = row['account_id'],
            transaction_type = TransactionType(row['transaction_type']),
            amount = row['amount'],
            description = row['description'],
            balance_after = row['balance_after'],
            timestamp = datetime.fromisoformat(row['timestamp']),
            status = TransactionStatus(row['status']),
            reference_number = row['reference_number']
        )
    