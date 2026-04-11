# ================================================
# src/db.py
# Database Connection Manager
# ================================================

import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ================================================
# Database Configuration
# ================================================
DB_CONFIG = {
    "host"     : os.getenv("DB_HOST", "localhost"),
    "port"     : os.getenv("DB_PORT", "5432"),
    "dbname"   : os.getenv("DB_NAME", "library_db"),
    "user"     : os.getenv("DB_USER", "postgres"),
    "password" : os.getenv("DB_PASSWORD", ""),
}

# ================================================
# Get Connection
# Returns a new database connection
# ================================================
def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"[DB ERROR] Could not connect to database: {e}")
        raise

# ================================================
# Get Cursor
# Returns a connection and cursor together
# Uses RealDictCursor so rows come back as dicts
# ================================================
def get_cursor():
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    return conn, cursor

# ================================================
# Test Connection
# Call this to verify DB is reachable
# ================================================
def test_connection():
    try:
        conn, cursor = get_cursor()
        cursor.execute("SELECT version();")
        result = cursor.fetchone()
        print(f"[DB OK] Connected to: {result['version']}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[DB FAIL] {e}")
        return False

# ================================================
# Run on file execute to verify connection
# ================================================
if __name__ == "__main__":
    test_connection()