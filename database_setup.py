import helpers
import sqlite3
import hashlib

DATABASE = "tweetor.db"




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
            hashtag TEXT NOT NULL,
            ip TEXT NOT NULL
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
        CREATE TABLE IF NOT EXISTS blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    blocker_handle TEXT NOT NULL,
    blocked_handle TEXT NOT NULL,
    block_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(blocker_handle, blocked_handle)
);
"""
)
def add_is_reflit_column_if_not_exists():
  db = helpers.get_db()
  cursor = db.cursor()

  # Check if the is_reflit column exists
  cursor.execute("PRAGMA table_info(flits)")
  columns = cursor.fetchall()
  column_names = [column[1] for column in columns]
  if 'is_reflit' not in column_names:
      # If the is_reflit column doesn't exist, add it
      cursor.execute("ALTER TABLE flits ADD COLUMN is_reflit INTEGER")
      db.commit()

  db.close()

def add_meme_link_column_if_not_exists():
   db = helpers.get_db()
   cursor = db.cursor()

   # Check if the meme_link column exists
   cursor.execute("PRAGMA table_info(flits)")
   columns = cursor.fetchall()
   column_names = [column[1] for column in columns]
   if 'meme_link' not in column_names:
       # If the meme_link column doesn't exist, add it
       cursor.execute("ALTER TABLE flits ADD COLUMN meme_link VARCHAR(255)")
       db.commit()

   db.close()


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

 # Check if the original_flit_id column exists
 cursor.execute("PRAGMA table_info(flits)")
 columns = cursor.fetchall()
 column_names = [column[1] for column in columns]
 if 'original_flit_id' not in column_names:
     # If the original_flit_id column doesn't exist, add it
     cursor.execute("ALTER TABLE flits ADD COLUMN original_flit_id INTEGER")
     db.commit()

 db.close()


create_admin_if_not_exists()
add_meme_link_column_if_not_exists()
add_is_reflit_column_if_not_exists()
add_original_flit_id_column_if_not_exists()
