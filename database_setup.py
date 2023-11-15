import helpers
import sqlite3
import hashlib

DATABASE = "tweetor.db"

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS flits  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL,
        meme_link TEXT
    )
"""
)


sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        turbo INTEGER DEFAULT 0,
        handle TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
"""
)

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS profane_flits  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL
    )
"""
)

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS flits  (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profane_flit TEXT,
            is_reflit INTEGER DEFAULT 0,
            userHandle TEXT NOT NULL,
            username TEXT NOT NULL,
            hashtag TEXT NOT NULL
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            turbo INTEGER DEFAULT 0,
            handle TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS direct_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_handle TEXT NOT NULL,
            receiver_handle TEXT NOT NULL,
            content TEXT,
            profane_dm TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reported_flits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            flit_id INTEGER NOT NULL,
            reporter_handle TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS blocked_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blocker TEXT NOT NULL,
            blocked TEXT NOT NULL,
            UNIQUE(blocker, blocked)
        )
    """
    )

def create_blocked_users_table_if_not_exists():
    db = helpers.get_db()
    cursor = db.cursor()
    
    # Check if the blocked_users table exists
    cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name='blocked_users'")
    
    # If the table doesn't exist, create it
    if cursor.fetchone()[0] != 1:
        cursor.execute(
            """
            CREATE TABLE blocked_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blocker TEXT NOT NULL,
                blocked TEXT NOT NULL,
                UNIQUE(blocker, blocked)
            )
            """
        )
        db.commit()
        print("Blocked users table created")

def add_is_reflit_column_if_not_exists():
    db = helpers.get_db()
    cursor = db.cursor()

    # Check if the is_reflit column exists in the flits table
    cursor.execute("PRAGMA table_info(flits)")
    columns = cursor.fetchall()

    # If the is_reflit column doesn't exist, add it
    if not any(column[1] == "is_reflit" for column in columns):
        cursor.execute(
            "ALTER TABLE flits ADD COLUMN is_reflit INTEGER DEFAULT 0"
        )
        db.commit()
        print("is_reflit column added to flits table")

def create_admin_if_not_exists():
  db = helpers.get_db()
  cursor = db.cursor()
  cursor.execute("SELECT * FROM users WHERE username = 'admin'")
  admin_account = cursor.fetchone()
  print("Admin account found:", admin_account)

  if not admin_account:
    hashed_password = hashlib.sha256("admin_password".encode()).hexdigest()
    cursor.execute(
      "INSERT INTO users (username, handle, password) VALUES (?, ?, ?)",
      ("admin", "admin", hashed_password),
    )
    db.commit()
    print("Admin account created")

def add_original_flit_id_column_if_not_exists():
    db = helpers.get_db()
    cursor = db.cursor()

    # Check if the original_flit_id column exists in the flits table
    cursor.execute("PRAGMA table_info(flits)")
    columns = cursor.fetchall()

    # If the original_flit_id column doesn't exist, add it
    if not any(column[1] == "original_flit_id" for column in columns):
        cursor.execute(
            "ALTER TABLE flits ADD COLUMN original_flit_id INTEGER DEFAULT -1"
        )
        db.commit()
        print("original_flit_id column added to flits table")

def add_profane_flit_column_if_not_exists():
    db = helpers.get_db()
    cursor = db.cursor()

    # Check if the profane_flit column exists in the flits table
    cursor.execute("PRAGMA table_info(flits)")
    columns = cursor.fetchall()

    # If the profane_flit column doesn't exist, add it
    if not any(column[1] == "profane_flit" for column in columns):
        cursor.execute(
            "ALTER TABLE flits ADD COLUMN profane_flit INTEGER DEFAULT 0"
        )
        db.commit()
        print("profane_flit column added to flits table")
create_admin_if_not_exists()
add_original_flit_id_column_if_not_exists()
add_is_reflit_column_if_not_exists()
create_blocked_users_table_if_not_exists()
add_profane_flit_column_if_not_exists()