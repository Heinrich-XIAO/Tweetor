import sqlite3
import hashlib
import random
from urllib.parse import quote
import string
import filters
import requests
import datetime
import time
import os
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    render_template,
    request,
    redirect,
    url_for,
    session,
    g,
    jsonify,
)
from flask_cors import CORS, cross_origin
from flask_session import Session
from sightengine.client import SightengineClient
from flask_sitemapper import Sitemapper

load_dotenv()
SIGHT_ENGINE_SECRET = os.getenv("SIGHT_ENGINE_SECRET")

app = Flask(__name__)
app.secret_key = "super secret key"
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"

sitemapper = Sitemapper()
sitemapper.init_app(app)

# Register the custom filters
app.jinja_env.filters["format_timestamp"] = filters.format_timestamp
app.jinja_env.filters["format_flit"] = filters.format_flit

# Set up the session object
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE = "tweetor.db"

staff_accounts = ["ItsMe", "Dude_Pog"]

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
    CREATE TABLE IF NOT EXISTS follows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        followerHandle TEXT NOT NULL,
        followingHandle TEXT NOT NULL
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


def get_db():
    db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db


def add_profanity_dm_column_if_not_exists():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(direct_messages)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if "profane_dm" not in column_names:
            cursor.execute("ALTER TABLE direct_messages ADD COLUMN profane_dm TEXT")
            db.commit()
            print("profane_dm column added to the direct_messages table")


def add_profanity_column_if_not_exists():
    with app.app_context():
        db = get_db()
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


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def create_admin_if_not_exists():
    with app.app_context():
        db = get_db()
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
    with app.app_context():
        db = get_db()
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


def row_to_dict(row):
    return {col[0]: row[idx] for idx, col in enumerate(row.description)}


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


@sitemapper.include()
@app.route("/")
def home() -> Response:
    # Get a connection to the database
    db = get_db()

    # Create a cursor to interact with the database
    cursor = db.cursor()

    # Check if the user is logged in and is an admin
    if "username" in session and session["handle"] == "admin":
        # If admin, retrieve all flits regardless of content
        cursor.execute("SELECT * FROM flits ORDER BY timestamp DESC")
    else:
        # If not admin, retrieve only non-profane flits
        cursor.execute(
            "SELECT * FROM flits WHERE profane_flit = 'no' ORDER BY timestamp DESC"
        )

    # Fetch the results of the SQL query
    flits = cursor.fetchall()

    # Check if the user is logged in
    if "username" in session:
        # Get the user's handle from the session
        user_handle = session["handle"]

        # Get the list of engaged direct messages for the user
        engaged_dms = get_engaged_direct_messages(user_handle)

        # Query the database to check if the user has turbo status
        cursor.execute("SELECT turbo FROM users WHERE handle = ?", (user_handle,))
        turbo = cursor.fetchone()["turbo"] == 1

        # Render the home template with user-specific data
        return render_template(
            "home.html",
            flits=flits,
            loggedIn=True,
            turbo=turbo,
            engaged_dms=engaged_dms,
        )
    else:
        # Render the home template without user-specific data since not logged in
        return render_template("home.html", flits=flits, loggedIn=False, turbo=False)


@app.route("/submit_flit", methods=["POST"])
def submit_flit() -> Response:
    # Get a connection to the database
    db = get_db()

    # Create a cursor to interact with the database
    cursor = db.cursor()

    # Check if the original_flit_id field is present in the form data
    if request.form.get("original_flit_id") is None:
        # Extract form data for the new flit
        content = str(request.form["content"])
        meme_url = request.form["meme_link"]

        # Validate meme URL format
        if not meme_url.startswith("https://media.tenor.com/") and meme_url != "":
            return render_template(
                "error.html", error="Why is this meme not from tenor?"
            )

        # Check if the user is muted
        if session.get("username") in muted:
            return render_template("error.html", error="You were muted.")

        # Check for various content validation conditions
        if content.strip() == "" and not meme_url:
            return render_template("error.html", error="Message was blank.")
        if len(content) > 10000:
            return render_template("error.html", error="Message was too long.")
        if "username" not in session:
            return render_template("error.html", error="You are not logged in.")

        # Check user's turbo status and content length/type
        cursor.execute("SELECT turbo FROM users WHERE handle = ?", (session["handle"],))
        user_turbo = cursor.fetchone()["turbo"]
        if user_turbo == 0 and (len(content) > 280 or "*" in content or "_" in content):
            return render_template("error.html", error="You do not have Tweetor Turbo.")

        # Extract and validate hashtag from form data
        hashtag = request.form["hashtag"]

        # Use the Sightengine result to check for profanity
        sightengine_result = is_profanity(content)
        profane_flit = "no"
        if (
            sightengine_result["status"] == "success"
            and len(sightengine_result["profanity"]["matches"]) > 0
        ):
            profane_flit = "yes"
            return render_template(
                "error.html", error="Do you really think that's appropriate?"
            )

        # Insert the new flit into the database
        cursor.execute(
            "INSERT INTO flits (username, content, userHandle, hashtag, profane_flit, meme_link, is_reflit, original_flit_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session["username"],
                content,
                session["handle"],
                hashtag,
                profane_flit,
                meme_url,
                0,
                -1,
            ),
        )
        db.commit()
        db.close()
        return redirect(url_for("home"))

    # Check for reflit
    is_reflit = False
    original_flit_id = request.form.get("original_flit_id")  # Get original_flit_id from form data
    if original_flit_id is not None:
        # Look for the original flit in the database
        cursor.execute("SELECT id FROM flits WHERE id = ?", (original_flit_id,))
        original_flit = cursor.fetchone()

        if original_flit:  # If the original flit exists
            is_reflit = True
            # Instead of using form content as new flit content, indicate it's a reflit
            content = "Reflit: " + str(original_flit_id)

    # Insert the reflit or empty flit into the database
    cursor.execute(
        "INSERT INTO flits (username, content, userHandle, hashtag, profane_flit, meme_link, is_reflit, original_flit_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            session["username"],
            "",
            session["handle"],
            "",
            "no",
            "",
            int(is_reflit),
            original_flit_id,
        ),
    )

    db.commit()
    db.close()
    return redirect(url_for("home"))


used_captchas = []


# Signup route
@sitemapper.include()
@app.route("/signup", methods=["GET", "POST"])
def signup() -> Response:
    error = None

    # If the HTTP request method is POST, handle form submission
    if request.method == "POST":
        username = request.form["username"].strip()
        handle = username
        password = request.form["password"]
        passwordConformation = request.form["passwordConformation"]
        user_captcha_input = request.form["input"]
        correct_captcha = request.form["correct_captcha"]

        # Prevent spam by checking if the captcha was already used
        if correct_captcha in used_captchas:
            return "Why did you try to spam accounts bruh?"
        used_captchas.append(correct_captcha)

        # Check if the user-provided captcha input matches the correct captcha
        if user_captcha_input != correct_captcha:
            return redirect("/signup")

        # Check if the provided passwords match
        if password != passwordConformation:
            return redirect("/signup")

        # Get a connection to the database
        db = get_db()

        # Create a cursor to interact with the database
        cursor = db.cursor()

        # Check if the username already exists in the database
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        
        # If the username is taken, modify the handle to make it unique
        if len(cursor.fetchall()) != 0:
            handle = f"{username}{len(cursor.fetchall())}"

        # Hash the password before storing it in the database
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Insert the new user data into the database
        cursor.execute(
            "INSERT INTO users (username, password, handle, turbo) VALUES (?, ?, ?, ?)",
            (username, hashed_password, handle, 0),
        )
        db.commit()
        db.close()

        # Set session data for the newly registered user
        session["handle"] = handle
        session["username"] = username

        # Redirect to the home page
        return redirect("/")

    # If the user is already logged in, redirect to the home page
    if "username" in session:
        return redirect("/")

    # Render the signup template with potential error messages
    return render_template("signup.html", error=error)


# Login route
@sitemapper.include()
@app.route("/login", methods=["GET", "POST"])
def login() -> Response:
    # Handle form submission if the request method is POST
    if request.method == "POST":
        handle = request.form["handle"]
        password = request.form["password"]

        # Get a connection to the database
        db = get_db()

        # Create a cursor to interact with the database
        cursor = db.cursor()

        # Query the database for the user with the provided handle
        cursor.execute("SELECT * FROM users WHERE handle = ?", (handle,))
        users = cursor.fetchall()

        # If there is no or more than one matching user, redirect to the login page
        if len(users) != 1:
            return redirect("/login")

        # Hash the provided password to check against the stored hashed password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # If the password matches the stored hashed password, set session data for the user
        if users[0]["password"] == hashed_password:
            session["handle"] = handle
            session["username"] = users[0]["username"]
        else:
            # If the password doesn't match, redirect to the login page
            return redirect("/login")

        # Redirect the user to the home page after successful login
        return redirect("/")

    # If the user is already logged in, redirect to the home page
    if "username" in session:
        return redirect("/")

    # Render the login template for users who are not logged in
    return render_template("login.html")

@app.route('/leaderboard')
def leaderboard():
    return render_template('leaderboard.html',
        loggedIn=("username" in session),
        engaged_dms=[]
        if "username" not in session
        else get_engaged_direct_messages(session["username"])
    )

c = sqlite3.connect(DATABASE).cursor()


def get_all_flit_ids():
    c.execute("SELECT id FROM flits")
    flit_ids = [i[0] for i in c.fetchall()]
    return flit_ids


@sitemapper.include(url_variables={"flit_id": get_all_flit_ids()})
@app.route("/flits/<flit_id>")
def singleflit(flit_id: str) -> Response:
    # Get a connection to the database
    conn = get_db()

    # Create a cursor to interact with the database
    c = conn.cursor()

    # Retrieve the specified flit's information from the database
    c.execute("SELECT * FROM flits WHERE id=?", (flit_id,))
    flit = c.fetchone()

    if flit:
        original_flit = None
        if flit["is_reflit"] == 1:
            # Retrieve the original flit's information if this flit is a reflit
            c.execute("SELECT * FROM flits WHERE id = ?", (flit["original_flit_id"],))
            original_flit = c.fetchone()

        if "username" in session:
            # If the user is logged in, check and update their interests in hashtags
            c.execute(
                "SELECT * FROM interests WHERE user=? AND hashtag=?",
                (
                    session["handle"],
                    flit["hashtag"],
                ),
            )
            interests = c.fetchall()

            # Update user's interest in the hashtag if it exists, otherwise add a new interest
            if len(interests) == 0:
                c.execute(
                    "INSERT INTO interests (user, hashtag, importance) VALUES (?, ?, ?)",
                    (
                        session["handle"],
                        flit["hashtag"],
                        1,
                    ),
                )
                conn.commit()
            else:
                c.execute(
                    "UPDATE interests SET importance=? WHERE user=? AND hashtag=?",
                    (
                        interests[0]["importance"] + 1,
                        session["handle"],
                        flit["hashtag"],
                    ),
                )
                conn.commit()

        # Render the template with the flit's information
        return render_template(
            "flit.html",
            flit=flit,
            loggedIn=("username" in session),
            original_flit=original_flit,
            engaged_dms=[]
            if "username" not in session
            else get_engaged_direct_messages(session["username"]),
        )

    # If the flit doesn't exist, redirect to the home page
    return redirect("/")


@app.route("/api/search", methods=["GET"])
def searchAPI() -> Response:
    if request.args.get("query"):
        conn = get_db()
        c = conn.cursor()

        # Find query
        c.execute(
            "SELECT * FROM flits WHERE content LIKE ?",
            (f"%{request.args.get('query')}%",),
        )
        flits = [dict(flit) for flit in c.fetchall()]
        return jsonify(flits)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM flits ORDER BY timestamp DESC")
    return jsonify([dict(flit) for flit in cursor.fetchall()])


@app.route("/search", methods=["GET"])
def search() -> Response:
    if request.args.get("query"):
        conn = get_db()
        c = conn.cursor()

        # Find query
        c.execute(
            "SELECT * FROM flits WHERE content LIKE ? OR hashtag LIKE ?",
            (
                f"%{request.args.get('query')}%",
                f"%{request.args.get('query')}%",
            ),
        )
        flits = [dict(flit) for flit in c.fetchall()]
        return render_template(
            "search.html",
            flits=flits,
            loggedIn=("username" in session),
            engaged_dms=[]
            if "username" not in session
            else get_engaged_direct_messages(session["username"]),
        )
    return render_template(
        "search.html",
        flits=False,
        loggedIn=("username" in session),
        engaged_dms=[]
        if "username" not in session
        else get_engaged_direct_messages(session["username"]),
    )


@app.route("/logout", methods=["GET", "POST"])
def logout() -> Response:
    # Check if the user is logged in
    if "username" in session:
        # Remove session data for the user
        session.pop("handle", None)
        session.pop("username", None)
    
    # Redirect the user to the home page, whether they were logged in or not
    return redirect("/")


def get_all_user_handles():
    c.execute("SELECT handle FROM users")
    user_handles = [i[0] for i in c.fetchall()]
    return user_handles


@sitemapper.include(url_variables={"username": get_all_user_handles()})
@app.route("/user/<path:username>")
def user_profile(username: str) -> Response:
    # Get a connection to the database
    conn = get_db()

    # Create a cursor to interact with the database
    cursor = conn.cursor()

    # Query the database for the user profile with the specified username
    cursor.execute("SELECT * FROM users WHERE handle = ?", (username,))
    user = cursor.fetchone()

    # If the user doesn't exist, redirect to the home page
    if not user:
        return redirect("/home")

    # Query the database for the user's non-reflit flits, ordered by timestamp
    cursor.execute(
        "SELECT * FROM flits WHERE userHandle = ? AND is_reflit=0 ORDER BY timestamp DESC",
        (username,),
    )
    flits = cursor.fetchall()

    # Check if the logged-in user is following this user's profile
    is_following = False
    if "username" in session:
        logged_in_username = session["username"]
        cursor.execute(
            "SELECT * FROM follows WHERE followerHandle = ? AND followingHandle = ?",
            (logged_in_username, user["handle"]),
        )
        is_following = cursor.fetchone() is not None

    # Calculate the user's activeness based on their tweet frequency
    latest_tweet_time = datetime.datetime.now()
    first_tweet_time = flits[-1]["timestamp"]
    first_tweet_time = datetime.datetime.strptime(first_tweet_time, "%Y-%m-%d %H:%M:%S")
    diff = latest_tweet_time - first_tweet_time
    weeks = diff.total_seconds() / 3600 / 24 / 7
    activeness = round(0 if weeks == 0 else len(flits) / weeks * 1000)

    # Initialize a list for user badges
    badges = []

    # Add badges based on activeness and staff status
    if activeness > 5000:
        badges.append(("badges/creator.png", "Activeness of over 5000"))

    if user["handle"] in staff_accounts:
        badges.append(("badges/staff.png", "Staff at Tweetor!"))

    # Render the user profile template with relevant data
    return render_template(
        "user.html",
        badges=badges,
        user=user,
        loggedIn=("username" in session),
        flits=flits,
        is_following=is_following,
        activeness=activeness,
        engaged_dms=[]
        if "username" not in session
        else get_engaged_direct_messages(session["username"]),
    )


@app.route("/like_flit", methods=["POST"])
def like_flit():
    flit_id = request.form["flitId"]
    user_handle = session["handle"]

    db = get_db()
    cursor = db.cursor()

    # Check if the like already exists
    cursor.execute(
        "SELECT * FROM likes WHERE userHandle = ? AND flitId = ?",
        (user_handle, flit_id),
    )
    existing_like = cursor.fetchone()

    if existing_like:
        # Unlike the flit
        cursor.execute("DELETE FROM likes WHERE id = ?", (existing_like["id"],))
    else:
        # Like the flit
        cursor.execute(
            "INSERT INTO likes (userHandle, flitId) VALUES (?, ?)",
            (user_handle, flit_id),
        )

    db.commit()

    return jsonify({"status": "success"})


@app.route("/follow_user", methods=["POST"])
def follow_user():
    try:
        if "followingUsername" not in request.form or "username" not in session:
            return render_template("error.html", error="You are not logged in.")
        following_username = request.form["followingUsername"]
        follower_username = session["username"]

        db = get_db()
        cursor = db.cursor()

        cursor.execute("SELECT * FROM users WHERE handle=?", (following_username,))

        if cursor.fetchone() is None:
            return render_template("error.html", error="That user doesn't exist.")

        # Check if the user is already following
        cursor.execute(
            "SELECT * FROM follows WHERE followerHandle = ? AND followingHandle = ?",
            (follower_username, following_username),
        )
        existing_follow = cursor.fetchone()

        if existing_follow:
            # Unfollow the user
            cursor.execute("DELETE FROM follows WHERE id = ?", (existing_follow["id"],))
        else:
            # Follow the user
            cursor.execute(
                "INSERT INTO follows (followerHandle, followingHandle) VALUES (?, ?)",
                (follower_username, following_username),
            )

        db.commit()

        return redirect(url_for("user_profile", username=following_username))
    except Exception as e:
        print(jsonify({"error": str(e)}), 500)
        return "Internal Server Error 500"


@app.route("/profanity")
def profanity() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template(
            "error.html", error="You are not authorized to view this page."
        )

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM flits WHERE profane_flit = 'yes' ORDER BY timestamp DESC"
    )
    profane_flit = cursor.fetchall()
    cursor.execute(
        """
        SELECT * FROM direct_messages WHERE profane_dm = "yes"
    """
    )
    profane_dm = cursor.fetchall()

    return render_template(
        "profanity.html", profane_flit=profane_flit, profane_dm=profane_dm
    )


def get_like_count(flit_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM likes WHERE flitId = ?", (flit_id,))
    return cursor.fetchone()["count"]


def get_follower_count(user_handle):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT COUNT(*) as count FROM follows WHERE followingHandle = ?",
        (user_handle,),
    )
    return cursor.fetchone()["count"]


def is_profanity(text):
    api_user = "570595698"
    api_secret = SIGHT_ENGINE_SECRET
    api_url = f"https://api.sightengine.com/1.0/text/check.json"

    data = {
        "text": text,
        "lang": "en",
        "mode": "standard",
        "api_user": api_user,
        "api_secret": api_secret,
        "categories": "drug,medical,extremism,weapon",
    }

    response = requests.post(api_url, data=data)
    result = response.json()

    return result  # Return the result instead of an empty list


@app.route("/delete_flit", methods=["GET"])
def delete_flit() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template(
            "error.html", error="You are not authorized to perform this action."
        )

    flit_id = request.args.get("flit_id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM flits WHERE id = ?", (flit_id,))
    cursor.execute("DELETE FROM reported_flits WHERE flit_id=?", (flit_id,))
    db.commit()

    return redirect(url_for("reported_flits"))


@app.route("/delete_user", methods=["POST"])
def delete_user() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template(
            "error.html", error="You are not authorized to perform this action."
        )

    user_handle = request.form["user_handle"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE handle = ?", (user_handle,))
    db.commit()

    return redirect(url_for("home"))


@app.route("/report_flit", methods=["POST"])
def report_flit():
    flit_id = request.form["flit_id"]
    reporter_handle = session["handle"]
    reason = request.form["reason"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO reported_flits (flit_id, reporter_handle, reason) VALUES (?, ?, ?)",
        (flit_id, reporter_handle, reason),
    )
    db.commit()

    return redirect(url_for("home"))


@app.route("/reported_flits")
def reported_flits():
    if "username" in session and session["handle"] != "admin":
        return render_template(
            "error.html", error="You don't have permission to access this page."
        )

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM reported_flits")
    reports = cursor.fetchall()

    return render_template("reported_flits.html", reports=reports)


@app.route("/dm/<path:receiver_handle>")
def direct_messages(receiver_handle):
    if "username" not in session:
        return render_template("error.html", error="You are not logged in.")

    sender_handle = session["handle"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT * FROM direct_messages
        WHERE (sender_handle = ? AND receiver_handle = ?)
        OR (sender_handle = ? AND receiver_handle = ?) AND profane_dm = 'no'
        ORDER BY timestamp DESC
    """,
        (sender_handle, receiver_handle, receiver_handle, sender_handle),
    )

    messages = cursor.fetchall()

    return render_template(
        "direct_messages.html",
        messages=messages,
        receiver_handle=receiver_handle,
        loggedIn="username" in session,
        engaged_dms=[]
        if "username" not in session
        else get_engaged_direct_messages(session["username"]),
    )


@app.route("/submit_dm/<path:receiver_handle>", methods=["POST"])
def submit_dm(receiver_handle):
    if "username" not in session:
        return render_template("error.html", error="You are not logged in.")

    sender_handle = session["handle"]
    content = request.form["content"]

    if len(content) > 1000:
        return render_template("error.html", error="Too many characters in DM")

    sightengine_result = is_profanity(content)
    profane_dm = "no"

    if (
        sightengine_result["status"] == "success"
        and len(sightengine_result["profanity"]["matches"]) > 0
    ):
        profane_dm = "yes"

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        INSERT INTO direct_messages (sender_handle, receiver_handle, content, profane_dm)
        VALUES (?, ?, ?, ?)
    """,
        (sender_handle, receiver_handle, content, profane_dm),
    )

    db.commit()

    send_notification(receiver_handle)

    return redirect(
        url_for(
            "direct_messages",
            receiver_handle=receiver_handle,
            loggedIn="username" in session,
        )
    )


muted = []


@app.route("/mute/<handle>")
def mute(handle):
    if session.get("handle") == "admin":
        muted.append(handle)
        return "Completed"


@app.route("/unmute/<handle>")
def unmute(handle):
    if session.get("handle") == "admin":
        muted.remove(handle)
        return "Completed"


clients = {}


def event_stream(user):
    while True:
        if (
            user in clients
            and (datetime.datetime.now() - clients[user]).total_seconds() <= 1
        ):
            # Generate the notification message
            data = "Someone sent you something"

            # Yield the data as an SSE event
            yield "data: {}\n\n".format(data)

        # Delay before sending the next event
        time.sleep(1)


@app.route("/stream")
def stream():
    user = session.get("handle")
    return Response(event_stream(user), mimetype="text/event-stream")


def send_notification(user):
    clients[user] = datetime.datetime.now()
    return "Notification sent"


@app.route("/get_captcha")
def get_captcha():
    while True:
        correct_captcha = "".join(
            random.choices(
                string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5
            )
        )
        if correct_captcha not in used_captchas:
            break
    return correct_captcha

@app.route("/api/flit")
def flitAPI():
    try:
        flit_id = int(request.args.get("flit_id"))
    except ValueError:
        return jsonify("Flit ID is invalid")
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM flits WHERE id=?', (flit_id,))
    flit = c.fetchone()
    
    if flit['profane_flit'] == 'yes':
        return "Flit is profane"
    
    return jsonify({
        "flit": dict(flit)
    })

if __name__ == "__main__":
    app.run(debug=False)
