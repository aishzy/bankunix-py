import os 
from pathlib import Path

class Config:
    """Base Configuration"""

    # Application
    APP_NAME = 'BankUnix'
    APP_VERSION = 'v.1.0.0'

    # Database
    DATABASE_PATH = Path(__file__).parent.parent / 'data' / 'banking.db'

    # Security
    MAX_FAILED_LOGIN_ATTEMPTS = 5
    ACCOUNT_LOCK_DURATION_MINUTES = 30
    PASSWORD_HASH_ALGORITHM = 'sha2256'

    # Validation 
    MIN_PASSWORD_LENGTH = 6
    MAX_ACCOUNT_NAME_LENGTH = 100
    MAX_TRANSACTION_AMOUNT = 1000000
    MIN_TRANSACTION_AMOUNT = 0.01

    # Features
    ENABLE_BILL_PAYMENT = True
    ENABLE_INTEREST_CALCULATION = True
    ENABLE_TRANSFER_LIMITS = True
    DAILY_TRANSFER_LIMIT = 50000

    # Logging 
    LOG_DIR = Path(__file__).parent.parent / 'logs'
    LOG_FILE = LOG_DIR / 'banking.db'
    LOG_LEVEL = 'INFO'

    # CLI 
    SHOW_ACCOUNT_DETAILS = True
    DEFAULT_STATEMENT_LIMIT = 10
    CURRENCY_SYMBOL = 'RM'
    CURRENCY_CODE = 'MYR'

    @classmethod
    def setup(cls):
        """Setup configuration"""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

class DevelopmentConfig(Config):
    """Development Configuration"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production Configuration"""
    DEBUG = False
    LOG_LEVEL = "WARNING"

def get_config() -> Config:
    """Get Configuration based on environment"""
    env = os.getenv('BANK_ENV', 'development')

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }

    return config_map.get(env, DevelopmentConfig)
