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
    CREATE TABLE IF NOT EXISTS interests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        hashtag TEXT NOT NULL,
        importance INT NOT NULL
    )
"""
)

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        origin TEXT NOT NULL,
        content TEXT NOT NULL,
        viewed INTEGER DEFAULT 0
    )
"""
)

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userHandle TEXT NOT NULL,
        flitId INTEGER NOT NULL
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


def add_profanity_dm_column_if_not_exists():
  db = helpers.get_db()
  cursor = db.cursor()
  cursor.execute("PRAGMA table_info(direct_messages)")
  columns = cursor.fetchall()
  column_names = [column[1] for column in columns]

  if "profane_dm" not in column_names:
    cursor.execute("ALTER TABLE direct_messages ADD COLUMN profane_dm TEXT")
    db.commit()
    print("profane_dm column added to the direct_messages table")


def add_profanity_column_if_not_exists():
  db = helpers.get_db()
  cursor = db.cursor()
  cursor.execute("PRAGMA table_info(flits)")
  columns = cursor.fetchall()
  column_names = [column[1] for column in columns]

  if "profane_flit" not in column_names:
      cursor.execute("ALTER TABLE flits ADD COLUMN profane_flit TEXT")
      db.commit()
      print("profane_flit column added to the flits table")


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

add_profanity_column_if_not_exists()

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
add_profanity_dm_column_if_not_exists()
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
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            hashtag TEXT NOT NULL,
            importance INT NOT NULL
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userHandle TEXT NOT NULL,
            flitd INTEGER NOT NULL
        )
    """
    )

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS follows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            followerHandle TEXT NOT NULL,
            followingHandle TEXT NOT NULL
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


def add_reflits_columns_if_not_exists():
  db = helpers.get_db()
  cursor = db.cursor()
  cursor.execute("PRAGMA table_info(flits)")
  columns = cursor.fetchall()
  column_names = [column[1] for column in columns]

  if "is_reflit" not in column_names:
    cursor.execute("ALTER TABLE flits ADD COLUMN is_reflit DEFAULT 0")
    print("is_reflit column added to the flits table")

  if "original_flit_id" not in column_names:
    cursor.execute(
      "ALTER TABLE flits ADD COLUMN original_flit_id INT DEFAULT -1"
    )
    print("original_flit_id column added to the flits table")

  db.commit()


add_reflits_columns_if_not_exists()