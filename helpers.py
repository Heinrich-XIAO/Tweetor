import sqlite3
from flask import (
  Flask,
  request,
  redirect,
  session,
  url_for,
  render_template  # added for admin_required
)
from functools import wraps
import os
import hashlib

DATABASE = "tweetor.db"
def get_db():
  db = sqlite3.connect(DATABASE)
  db.row_factory = sqlite3.Row
  return db

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'), 302)
        return f(*args, **kwargs)
    return decorated_function

def get_client_ip():
    forwarded = request.headers.getlist("X-Forwarded-For")
    return forwarded[0] if forwarded else request.headers.get('cf-connecting-ip') or request.remote_addr

def get_all_user_handles():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT handle FROM users")
        return [row[0] for row in cursor.fetchall()]

def get_user_handle():
  db = get_db()
  cursor = db.cursor()
  if "username" not in session:
        return "Not Logged In"
  else:
        return session["handle"]

def get_all_flit_ids():
    with get_db() as db:
        cursor = db.cursor()
        cursor.execute("SELECT id FROM flits")
        return [row[0] for row in cursor.fetchall()]

def get_blocked_users(current_user_handle):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT blocked_handle FROM blocks WHERE blocker_handle = ?
        """, (current_user_handle,))
        blocked_users = cursor.fetchall()
    return [row[0] for row in blocked_users]

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
