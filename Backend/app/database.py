"""
database.py  —  MySQL connection factory
-----------------------------------------
Reads DB credentials from Backend/.env file.
Every API route calls get_connection() to get a fresh connection,
uses it, then closes it in the finally block.
"""

import os
import mysql.connector
from dotenv import load_dotenv

# Walk up one level from app/ to Backend/ to find .env
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def get_connection():
    return mysql.connector.connect(
        host     = os.getenv("DB_HOST", "localhost"),
        user     = os.getenv("DB_USER", "root"),
        password = os.getenv("DB_PASSWORD", "root"),
        database = os.getenv("DB_NAME", "hostelhub")
    )
