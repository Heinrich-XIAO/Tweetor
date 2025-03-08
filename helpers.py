import sqlite3
from flask import (
  Flask,
  request,
  redirect,
  session,
  url_for,
)
from functools import wraps
import os
import hashlib

DATABASE = "tweetor.db"
def get_db():
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  return db

def get_engaged_direct_messages(user_handle):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT DISTINCT receiver_handle FROM direct_messages
        WHERE sender_handle = ?
        UNION
        SELECT DISTINCT sender_handle FROM direct_messages
        WHERE receiver_handle = ?
    """,
        (user_handle, user_handle),
    )

    engaged_dms = cursor.fetchall()

    db.commit()

    return engaged_dms

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'), 302)
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    elif request.remote_addr != "127.0.0.1":
        ip = request.remote_addr
    else:
        ip = request.headers.get('cf-connecting-ip')

    return ip

def get_all_user_handles():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT handle FROM users")
    user_handles = [i[0] for i in cursor.fetchall()]
    return user_handles


def get_user_handle():
  db = get_db()
  cursor = db.cursor()
  if "username" not in session:
        return "Not Logged In"
  else:
        return session["handle"]
def get_all_flit_ids():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT id FROM flits")
    flit_ids = [i[0] for i in cursor.fetchall()]
    return flit_ids

def get_blocked_users(current_user_handle):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT blocked_handle FROM blocks WHERE blocker_handle = ?
    """, (current_user_handle,))
    blocked_users = cursor.fetchall()
    conn.close()

    # Convert the result to a list of usernames
    blocked_usernames = [row[0] for row in blocked_users]
    return blocked_usernames

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the user is logged in
        if 'username' not in session:
            return redirect(url_for('login'))  # Redirect to login page if not logged in
        
        # Check if the user is not an admin
        if session['handle'] != 'admin':
            return render_template(
                "error.html", error="You are not authorized to perform this action."
            )
        
        # If the user is logged in and is not an admin, call the original function
        return f(*args, **kwargs)
    return decorated_function


def testing_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the application is running in a testing environment
        if os.getenv('TESTING') is None:
            return "Not in testing mode.", 403  # Return an error if not in testing mode
        
        # If in testing mode, proceed to call the original function
        return f(*args, **kwargs)
    return decorated_function