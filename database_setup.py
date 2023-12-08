import helpers
import sqlite3
import hashlib

DATABASE = "tweetor.db"

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

create_admin_if_not_exists()