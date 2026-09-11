"""
Configuration Settings Module 
=============================
This module contains all configuration constants and settings for the banking system.
These settings are used across all layers of the application.
"""

APP_CONFIG = {
    'APP_NAME': 'BankUnix Banking System',
    'APP_VERSION': 'v.1.0.0',
    'DATABASE_PATH': 'bankunix_data.db',
    'MIN_BALANCE': 0,
    'MAX_TRANSACTION_AMOUNT': 100000,
    'MIN_TRANSACTION_AMOUNT': 0.01,
    'MONTHLY_INTEREST_RATE': 0.05,  # Interest rate per month for savings accounts (as decimal, e.g., 0.05 = 5%)
    'OVERDRAFT_PENALTY': 50,        # Penalty fee for overdraft attempts (when balance would go negative)
    'DAILY_TRANSACTION_LIMIT': 20,  # Daily transaction limit - Maximum number of transactions per day
    'CURRENCY_SYMBOL': 'RM',
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S', # Date format for displaying dates to users  
}


# Transaction type constants used throughout the system
TRANSACTION_TYPE = {
    'DEPOSIT': 'DEPOSIT',
    'WITHDRAWAL': 'WITHDRAWAL',
    'TRANSFER': 'TRANSFER',
    'INTEREST': 'INTEREST',
    'PENALTY': 'PENALTY',
}

# Account types constants 
ACCOUNT_TYPES = {
    'CHECKING': 'CHECKING', # Regular checking account with standard features
    'SAVINGS': 'SAVINGS',   # Savings account that earn interest 
}

# Account status constants 
ACCOUNT_STATUS = {
    'ACTIVE': 'ACTIVE',
    'FROZEN': 'FROZEN',
    'CLOSED': 'CLOSED',
}