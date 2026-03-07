"""
Environment configuration - loaded once, used everywhere
"""
import os

# Load and validate Argon2 parameters
PASSWORD_HASHER_TIME_COST = int(os.getenv('PASSWORD_HASHER_TIME_COST', '2'))
PASSWORD_HASHER_MEMORY_COST = int(os.getenv('PASSWORD_HASHER_MEMORY_COST', '65536'))
PASSWORD_HASHER_PARALLELISM = int(os.getenv('PASSWORD_HASHER_PARALLELISM', '4'))

# Database
MYSQL_USER     = str(os.getenv('MYSQL_USER', 'docstore'))
MYSQL_PASSWORD = str(os.getenv('MYSQL_PASSWORD'))
MYSQL_HOST     = str(os.getenv('MYSQL_HOST', 'docstore'))
MYSQL_PORT     = int(os.getenv('MYSQL_PORT', 3306))
MYSQL_DB       = str(os.getenv('MYSQL_DB', 'docstore'))

SQLALCHEMY_TRACK_MODIFICATIONS = bool(os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', True))

SQLALCHEMY_ENGINE_OPTIONS = dict()
SQLALCHEMY_ENGINE_OPTIONS["pool_pre_ping"] = bool(os.getenv('SQLALCHEMY_ENGINE_OPTIONS_POOL_PRE_PING', True))
SQLALCHEMY_ENGINE_OPTIONS["pool_recycle"] = int(os.getenv('SQLALCHEMY_ENGINE_OPTIONS_POOL_RECYCLE', 3600))
SQLALCHEMY_ENGINE_OPTIONS["pool_timeout"] = int(os.getenv('SQLALCHEMY_ENGINE_OPTIONS_POOL_TIMEOUT', 30))
SQLALCHEMY_ENGINE_OPTIONS["pool_size"] = int(os.getenv('SQLALCHEMY_ENGINE_OPTIONS_POOL_SIZE', 5))
SQLALCHEMY_ENGINE_OPTIONS["max_overflow"] = int(os.getenv('SQLALCHEMY_ENGINE_OPTIONS_MAX_OVERFLOW', 10))

# App security
SECRET_KEY = os.getenv('SECRET_KEY')

# FAIL-FAST: Check required vars
REQUIRED_VARS = ['MYSQL_PASSWORD', 'SECRET_KEY']
missing = [var for var in REQUIRED_VARS if not os.getenv(var)]
if missing:
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}.\n"
                    f"Add to .env:\n"
                    f"  MYSQL_PASSWORD=your_password\n"
                    f"  SECRET_KEY=your-super-secret-key-at-least-32-chars")