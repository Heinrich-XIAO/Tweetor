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
from flask import Flask, Response, render_template, request, redirect, url_for, session, g, jsonify
from flask_cors import CORS, cross_origin
from flask_session import Session
from sightengine.client import SightengineClient

load_dotenv()
SIGHT_ENGINE_SECRET = os.getenv('SIGHT_ENGINE_SECRET')

app = Flask(__name__)
app.secret_key = "super secret key"
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# Register the custom filters
app.jinja_env.filters['format_timestamp'] = filters.format_timestamp
app.jinja_env.filters['format_tweet'] = filters.format_tweet

# Set up the session object
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

DATABASE = "tweetor.db"

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS tweets  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL,
        meme_link TEXT
    )
""")


sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        turbo INTEGER DEFAULT 0,
        handle TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
""")

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS interests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        hashtag TEXT NOT NULL,
        importance INT NOT NULL
    )
""")

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT NOT NULL,
        origin TEXT NOT NULL,
        content TEXT NOT NULL,
        viewed INTEGER DEFAULT 0
    )
""")

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        userHandle TEXT NOT NULL,
        tweetId INTEGER NOT NULL
    )
""")

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS follows (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        followerHandle TEXT NOT NULL,
        followingHandle TEXT NOT NULL
    )
""")

sqlite3.connect(DATABASE).cursor().execute(
    """
    CREATE TABLE IF NOT EXISTS profane_tweets  (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        userHandle TEXT NOT NULL,
        username TEXT NOT NULL,
        hashtag TEXT NOT NULL
    )
""")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
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

        if 'profane_dm' not in column_names:
            cursor.execute("ALTER TABLE direct_messages ADD COLUMN profane_dm TEXT")
            db.commit()
            print("profane_dm column added to the direct_messages table")


def add_profanity_column_if_not_exists():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(tweets)")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]

        if 'profane_tweet' not in column_names:
            cursor.execute("ALTER TABLE tweets ADD COLUMN profane_tweet TEXT")
            db.commit()
            print("profane_tweet column added to the tweets table")

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tweets  (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            profane_tweet TEXT,
            userHandle TEXT NOT NULL,
            username TEXT NOT NULL,
            hashtag TEXT NOT NULL
        )
    """)

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
    """)

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
    """)
add_profanity_dm_column_if_not_exists()
with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS reported_tweets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tweet_id INTEGER NOT NULL,
            reporter_handle TEXT NOT NULL,
            reason TEXT NOT NULL
        )
    """)
    

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS interests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            hashtag TEXT NOT NULL,
            importance INT NOT NULL
        )
    """)

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userHandle TEXT NOT NULL,
            tweetId INTEGER NOT NULL
        )
    """)

with sqlite3.connect(DATABASE) as conn:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS follows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            followerHandle TEXT NOT NULL,
            followingHandle TEXT NOT NULL
        )
    """)

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
            cursor.execute("INSERT INTO users (username, handle, password) VALUES (?, ?, ?)", ("admin", "admin", hashed_password))
            db.commit()
            print("Admin account created")

create_admin_if_not_exists()

def row_to_dict(row):
    return {col[0]: row[idx] for idx, col in enumerate(row.description)}

def get_engaged_direct_messages(user_handle):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT DISTINCT receiver_handle FROM direct_messages
        WHERE sender_handle = ?
        UNION
        SELECT DISTINCT sender_handle FROM direct_messages
        WHERE receiver_handle = ?
    """, (user_handle, user_handle))

    engaged_dms = cursor.fetchall()
    return engaged_dms


@app.route("/")
def home() -> Response:
    db = get_db()
    cursor = db.cursor()    
    if "username" in session and session["handle"] == "admin":
        cursor.execute("SELECT * FROM tweets ORDER BY timestamp DESC")
    else:
        cursor.execute("SELECT * FROM tweets WHERE profane_tweet = 'no' ORDER BY timestamp DESC")
          
    tweets = cursor.fetchall()

    if "username" in session:
        user_handle = session["handle"]
        engaged_dms = get_engaged_direct_messages(user_handle)

        cursor.execute("SELECT turbo FROM users WHERE handle = ?", (user_handle, ))
        turbo = cursor.fetchone()["turbo"] == 1

        return render_template("home.html", tweets=tweets, loggedIn=True, turbo=turbo, engaged_dms=engaged_dms)
    else:
        return render_template("home.html", tweets=tweets, loggedIn=False, turbo=False)

@app.route("/submit_tweet", methods=["POST"])
def submit_tweet() -> Response:
    content = str(request.form["content"])
    meme_template_id = request.form["template_id"]
    meme_text0 = request.form["text0"]
    meme_text1 = request.form["text1"]
    if session.get("username") in muted:
        return render_template("error.html", error="You were muted.")
    if content.strip() == "":
        return render_template("error.html", error="Message was blank.")
    if len(content) > 10000:
        return render_template("error.html", error="Message was too long.")
    if "username" not in session:
        return render_template("error.html", error="You are not logged in.")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT turbo FROM users WHERE handle = ?", (session["handle"], ))
    user_turbo = cursor.fetchone()["turbo"]
    
    if user_turbo == 0 and (len(content) > 280 or "*" in content or "_" in content):
        return render_template("error.html", error="You do not have Tweetor Turbo.")
    
    hashtag = request.form["hashtag"]
    
    # Use the Sightengine result directly to check for profanity
    sightengine_result = is_profanity(content+" "+meme_text0+" "+meme_text1)
    profane_tweet = "no"
    
    if sightengine_result['status'] == 'success' and len(sightengine_result['profanity']['matches']) > 0:
        profane_tweet = "yes"
        return render_template("error.html", error="Do you really think that's appropriate?")
    
    meme_url = None
    
    if meme_template_id and meme_text0 and meme_text1:
        # IMGFLIP image generating
        r = requests.post("https://api.imgflip.com/caption_image", data={
        'template_id': meme_template_id,
        'username': "tweetor_official",
        'password': "tweetor_password",
        'text0': meme_text0,
        'text1': meme_text1
        })

        json = r.json()

        print(json)
        if json["success"]:
            meme_url = json['data']['url']
    
    # Insert the tweet into the database
    cursor.execute("INSERT INTO tweets (username, content, userHandle, hashtag, profane_tweet, meme_link) VALUES (?, ?, ?, ?, ?, ?)", (session["username"], content, session["handle"], hashtag, profane_tweet, meme_url, ))
    
    db.commit()
    return redirect(url_for('home'))

# Signup route
@app.route("/signup", methods=["GET", "POST"])
def signup() -> Response:
    error = None
    correct_captcha = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=5))
    if request.method == "POST":
        username = request.form["username"]
        handle = username
        password = request.form["password"]
        passwordConformation = request.form["passwordConformation"]
        user_captcha_input = request.form["input"]
        correct_captcha = request.form["correct_captcha"]

        if user_captcha_input != correct_captcha:
            return redirect("/signup")

        if password != passwordConformation:
            return redirect("/signup")

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

        if len(cursor.fetchall()) != 0:
            handle = f"{username}{len(cursor.fetchall())}"

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO users (username, password, handle, turbo) VALUES (?, ?, ?, ?)",
            (username, hashed_password, handle, 0),
        )
        db.commit()
        db.close()

        session["handle"] = handle
        session["username"] = username
        return redirect("/")

    if "username" in session:
        return redirect("/")
    return render_template("signup.html", error=error, correct_captcha=correct_captcha)


# Login route
@app.route("/login", methods=["GET", "POST"])
def login() -> Response:
    if request.method == "POST":
        handle = request.form["handle"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE handle = ?", (handle,))

        users = cursor.fetchall()
        if len(users) != 1:
            return redirect("/login")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if users[0]["password"] == hashed_password:
            session["handle"] = handle
            session["username"] = users[0]["username"]
        else:
            return redirect("/login")
        return redirect("/")
    
    if "username" in session:
        return redirect("/")
    return render_template("login.html")



@app.route('/tweets/<tweet_id>')
def singleTweet(tweet_id: str) -> Response:
    conn = get_db()
    c = conn.cursor()

    # Get the tweet's information from the database
    c.execute("SELECT * FROM tweets WHERE id=?", (tweet_id,))
    tweet = c.fetchone()

    if tweet:
        if "username" in session:
            conn = get_db()
            c = conn.cursor()
            c.execute("SELECT * FROM interests WHERE user=? AND hashtag=?", (session["handle"], tweet["hashtag"], ))
            interests = c.fetchall()
            if len(interests) == 0:
                conn = get_db()
                c = conn.cursor()
                c.execute("INSERT INTO interests (user, hashtag, importance) VALUES (?, ?, ?)", (
                    session["handle"],
                    tweet["hashtag"],
                    1,
                ))

                conn.commit()
                conn.close()
            else:
                conn = get_db()
                c = conn.cursor()
                c.execute("UPDATE interests SET importance=? WHERE user=? AND hashtag=?", (
                    interests[0]["importance"]+1,
                    session["handle"],
                    tweet["hashtag"],
                ))
                conn.commit()
                conn.close()

        # Render the template with the tweet's information
        return render_template("tweet.html", tweet=tweet, loggedIn=("username" in session))

    # If the user doesn't exist, display an error message
    return redirect("/")

@app.route('/api/search', methods=["GET"])
def searchAPI() -> Response:
    if request.args.get("query"):
        conn = get_db()
        c = conn.cursor()

        # Find query
        c.execute("SELECT * FROM tweets WHERE content LIKE ?", (f"%{request.args.get('query')}%", ))
        tweets = [dict(tweet) for tweet in c.fetchall()]
        return jsonify(tweets)
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tweets ORDER BY timestamp DESC")
    return jsonify([dict(tweet) for tweet in cursor.fetchall()])

@app.route('/search', methods=["GET"])
def search() -> Response:
    if request.args.get("query"):
        conn = get_db()
        c = conn.cursor()

        # Find query
        c.execute("SELECT * FROM tweets WHERE content LIKE ? OR hashtag LIKE ?", (f"%{request.args.get('query')}%", f"%{request.args.get('query')}%", ))
        tweets = [dict(tweet) for tweet in c.fetchall()]
        return render_template("search.html", tweets=tweets, loggedIn=("username" in session))
    return render_template("search.html", tweets=False, loggedIn=("username" in session))

@app.route('/logout', methods=["GET", "POST"])
def logout() -> Response:
    if "username" in session:
        session.pop('handle', None)
        session.pop('username', None)
    return redirect("/")


@app.route("/user/<username>")
def user_profile(username: str) -> Response:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if not user:
        return redirect("/home")

    cursor.execute("SELECT * FROM tweets WHERE userHandle = ?", (username, ))
    tweets = cursor.fetchall()

    is_following = False
    if "username" in session:
        logged_in_username = session["username"]
        cursor.execute("SELECT * FROM follows WHERE followerHandle = ? AND followingHandle = ?", (logged_in_username, user["handle"]))
        is_following = cursor.fetchone() is not None

    return render_template("user.html", user=user, loggedIn=("username" in session), tweets=tweets, is_following=is_following)

@app.route("/like_tweet", methods=["POST"])
def like_tweet():
    tweet_id = request.form["tweetId"]
    user_handle = session["handle"]

    db = get_db()
    cursor = db.cursor()

    # Check if the like already exists
    cursor.execute("SELECT * FROM likes WHERE userHandle = ? AND tweetId = ?", (user_handle, tweet_id))
    existing_like = cursor.fetchone()

    if existing_like:
        # Unlike the tweet
        cursor.execute("DELETE FROM likes WHERE id = ?", (existing_like["id"],))
    else:
        # Like the tweet
        cursor.execute("INSERT INTO likes (userHandle, tweetId) VALUES (?, ?)", (user_handle, tweet_id))

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

        cursor.execute("SELECT * FROM users WHERE handle=?", (following_username, ))

        if cursor.fetchone() is None:
            return render_template("error.html", error="That user doesn't exist.")

        # Check if the user is already following
        cursor.execute("SELECT * FROM follows WHERE followerHandle = ? AND followingHandle = ?", (follower_username, following_username))
        existing_follow = cursor.fetchone()

        if existing_follow:
            # Unfollow the user
            cursor.execute("DELETE FROM follows WHERE id = ?", (existing_follow["id"],))
        else:
            # Follow the user
            cursor.execute("INSERT INTO follows (followerHandle, followingHandle) VALUES (?, ?)", (follower_username, following_username))

        db.commit()

        return redirect(url_for("user_profile", username=following_username))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/profanity")
def profanity() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template("error.html", error="You are not authorized to view this page.")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tweets WHERE profane_tweet = 'yes' ORDER BY timestamp DESC")
    profane_tweet = cursor.fetchall()
    cursor.execute("""
        SELECT * FROM direct_messages WHERE profane_dm = "yes"
    """)
    profane_dm = cursor.fetchall()

    return render_template("profanity.html", profane_tweet=profane_tweet, profane_dm=profane_dm)

def get_like_count(tweet_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM likes WHERE tweetId = ?", (tweet_id,))
    return cursor.fetchone()["count"]

def get_follower_count(user_handle):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM follows WHERE followingHandle = ?", (user_handle,))
    return cursor.fetchone()["count"]

def is_profanity(text):
    api_user = '570595698'
    api_secret = SIGHT_ENGINE_SECRET
    api_url = f'https://api.sightengine.com/1.0/text/check.json?text={quote(text)}&lang=en&mode=standard&categories=drug%2Cmedical%2Cextremism%2Cweapon'
    
    data = {
        'text': text,
        'lang': 'en',
        'mode': 'standard',
        'api_user': api_user,
        'api_secret': api_secret,
    }
    
    params = {
        'categories': 'drug,medical,extremism,weapon'
    }

    response = requests.post(api_url, data=data, params=params)
    result = response.json()
    
    print(f"Sightengine result: {result}")  # Debugging: Print the result

    return result  # Return the result instead of an empty list

@app.route("/delete_tweet", methods=["GET"])
def delete_tweet() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template("error.html", error="You are not authorized to perform this action.")

    tweet_id = request.args.get("tweet_id")
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tweets WHERE id = ?", (tweet_id,))
    cursor.execute("DELETE FROM reported_tweets WHERE tweet_id=?", (tweet_id,))
    db.commit()

    return redirect(url_for("reported_tweets"))


@app.route("/delete_user", methods=["POST"])
def delete_user() -> Response:
    if "username" in session and session["handle"] != "admin":
        return render_template("error.html", error="You are not authorized to perform this action.")

    user_handle = request.form["user_handle"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE handle = ?", (user_handle,))
    db.commit()

    return redirect(url_for("home"))

@app.route("/report_tweet", methods=["POST"])
def report_tweet():
    tweet_id = request.form["tweet_id"]
    reporter_handle = session["handle"]
    reason = request.form["reason"]

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO reported_tweets (tweet_id, reporter_handle, reason) VALUES (?, ?, ?)", (tweet_id, reporter_handle, reason))
    db.commit()

    return redirect(url_for("home"))

@app.route("/reported_tweets")
def reported_tweets():
    if "username" in session and session["handle"] != "admin":
        return render_template("error.html", error="You don't have permission to access this page.")

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM reported_tweets")
    reports = cursor.fetchall()

    return render_template("reported_tweets.html", reports=reports)

@app.route('/dm/<receiver_handle>')
def direct_messages(receiver_handle):
    if "username" not in session:
        return render_template("error.html", error="You are not logged in.")
    
    sender_handle = session["handle"]

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT * FROM direct_messages
        WHERE (sender_handle = ? AND receiver_handle = ?)
        OR (sender_handle = ? AND receiver_handle = ?) AND profane_dm = 'no'
        ORDER BY timestamp DESC
    """, (sender_handle, receiver_handle, receiver_handle, sender_handle))

    messages = cursor.fetchall()

    return render_template("direct_messages.html", messages=messages, receiver_handle=receiver_handle, loggedIn="username"in session)

@app.route("/submit_dm/<receiver_handle>", methods=["POST"])
def submit_dm(receiver_handle):
    if "username" not in session:
        return render_template("error.html", error="You are not logged in.")
    
    sender_handle = session["handle"]
    content = request.form["content"]

    sightengine_result = is_profanity(content)
    profane_dm = "no"

    if sightengine_result['status'] == 'success' and len(sightengine_result['profanity']['matches']) > 0:
        profane_dm = "yes"

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO direct_messages (sender_handle, receiver_handle, content, profane_dm)
        VALUES (?, ?, ?, ?)
    """, (sender_handle, receiver_handle, content, profane_dm))

    db.commit()

    send_notification(receiver_handle)

    return redirect(url_for("direct_messages", receiver_handle=receiver_handle, loggedIn="username"in session))

muted = []

@app.route('/mute/<handle>')
def mute(handle):
    if session.get('handle') == 'admin':
        muted.append(handle)
        return "Completed"

@app.route('/unmute/<handle>')
def unmute(handle):
    if session.get('handle') == 'admin':
        muted.remove(handle)
        return "Completed"

clients = {}

def event_stream(user):
    while True:
        if user in clients and (datetime.datetime.now() - clients[user]).total_seconds()<=1:
            # Generate the notification message
            data = 'Someone sent you something'

            # Yield the data as an SSE event
            yield 'data: {}\n\n'.format(data)

        # Delay before sending the next event
        time.sleep(1)

@app.route('/stream')
def stream():
    user = session.get('handle')
    return Response(event_stream(user), mimetype='text/event-stream')

def send_notification(user):
    clients[user] = datetime.datetime.now()
    return 'Notification sent'

if __name__ == "__main__":
    app.run(debug=False)