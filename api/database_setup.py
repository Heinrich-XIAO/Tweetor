import sqlite3
import hashlib
import psycopg2
from psycopg2 import sql
import os

# Retrieve database connection parameters from environment variables
DATABASE = os.environ.get("DB_NAME", "postgres")
USER = os.environ.get("DB_USER")
PASSWORD = os.environ.get("DB_PASSWORD")
HOST = os.environ.get("DB_HOST", "localhost")
PORT = os.environ.get("DB_PORT", "5432")

def get_db():
    connection_params = {
        "dbname": DATABASE,
        "user": USER,
        "password": PASSWORD,
        "host": HOST,
        "port": PORT
    }
    db = psycopg2.connect(**connection_params)
    db.autocommit = True
    return db

# Define the table creation queries
table_queries = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        turbo INTEGER DEFAULT 0,
        handle TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS profane_flits (
        id SERIAL PRIMARY KEY,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS flits (
        id SERIAL PRIMARY KEY,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        profane_flit TEXT,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL,
        is_reflit INTEGER,
        meme_link VARCHAR(255),
        original_flit_id INTEGER
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS direct_messages (
        id SERIAL PRIMARY KEY,
        sender_handle TEXT NOT NULL,
        receiver_handle TEXT NOT NULL,
        content TEXT,
        profane_dm TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS reported_flits (
        id SERIAL PRIMARY KEY,
        flit_id INTEGER NOT NULL,
        reporter_handle TEXT NOT NULL,
        reason TEXT NOT NULL
    )
    """
]

# Function to execute table creation queries
def create_tables():
    with get_db() as conn:
        with conn.cursor() as cursor:
            for query in table_queries:
                cursor.execute(query)

# Functions to add columns if they don't exist
def add_is_reflit_column_if_not_exists():
    with get_db() as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'flits' AND column_name = 'is_reflit'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE flits ADD COLUMN is_reflit INTEGER")

def add_meme_link_column_if_not_exists():
    with get_db() as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'flits' AND column_name = 'meme_link'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE flits ADD COLUMN meme_link VARCHAR(255)")

def add_original_flit_id_column_if_not_exists():
    with get_db() as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'flits' AND column_name = 'original_flit_id'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE flits ADD COLUMN original_flit_id INTEGER")

# Function to create admin account if not exists
def create_admin_if_not_exists():
    with get_db() as db:
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            admin_account = cursor.fetchone()
            print("Admin account found:", admin_account)

            if not admin_account:
                hashed_password = hashlib.sha256("admin_password".encode()).hexdigest()
                cursor.execute(
                    "INSERT INTO users (username, handle, password) VALUES (%s, %s, %s)",
                    ("admin", "admin", hashed_password),
                )
                print("Admin account created")

# Execute table creation queries
create_tables()

# Execute functions to add columns if they don't exist
add_is_reflit_column_if_not_exists()
add_meme_link_column_if_not_exists()
add_original_flit_id_column_if_not_exists()

# Create admin account if not exists
create_admin_if_not_exists()
