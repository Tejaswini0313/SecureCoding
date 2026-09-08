from flask import Flask, request, render_template_string, session, redirect
import sqlite3
from time import time
from dotenv import load_dotenv
import os

from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 60

login_attempts = {}

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "secure_users.db")

@app.after_request
def add_security_headers(response):

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self'; "
        "object-src 'none'; "
        "frame-ancestors 'none';"
    )

    return response

def get_db():
    connection = sqlite3.connect(DATABASE)
    return connection


def create_database():

    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)

    connection.commit()
    connection.close()


@app.route("/")
def home():

    return """
    <h1>Secure Coding Review</h1>

    <hr>

    <h2>Create Account</h2>

    <form action="/register" method="POST">

        Username:
        <input type="text" name="username" maxlength="50" required>

        <br><br>

        Password:
        <input type="password" name="password" maxlength="128" required>

        <br><br>

        <button type="submit">
            Register
        </button>

    </form>

    <h2>Secure Login</h2>
    
        <form action="/login" method="POST">
    
            Username:
            <input type="text" name="username">
    
            <br><br>
    
            Password:
            <input type="password" name="password">
    
            <br><br>
    
            <button type="submit">
                Login
            </button>
    
        </form>
    
        <hr>

    <h2>Comment Section</h2>

    <form action="/comment" method="GET">

        Comment:
        <input type="text" name="comment">

        <button type="submit">
            Submit Comment
        </button>

    </form>
    """

@app.route("/register", methods=["POST"])
def register():

    username = request.form.get(
        "username",
        ""
    ).strip()

    password = request.form.get(
        "password",
        ""
    )

    # Validate username and password

    if not username or not password:
        return "<h2>Username and password are required.</h2>", 400

    if len(username) > 50:
        return "<h2>Username is too long.</h2>", 400

    if len(password) > 128:
        return "<h2>Password is too long.</h2>", 400

    if len(password) < 8:
        return "<h2>Password must contain at least 8 characters.</h2>", 400

    connection = get_db()

    # Check whether username already exists

    existing_user = connection.execute(
        "SELECT id FROM users WHERE username = ?",
        (username,)
    ).fetchone()

    if existing_user:

        connection.close()

        return "<h2>Username already exists.</h2>", 409

    # Hash the password before storing it

    password_hash = generate_password_hash(password)

    connection.execute(
        """
        INSERT INTO users
        (username, password_hash)
        VALUES (?, ?)
        """,
        (username, password_hash)
    )

    connection.commit()
    connection.close()

    return "<h2>Account created successfully. You can now log in.</h2>"

@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return "<h2>Username and password are required.</h2>", 400

    if len(username) > 50 or len(password) > 128:
        return "<h2>Input is too long.</h2>", 400

    current_time = time()

    # Check whether this username is temporarily locked
    if username in login_attempts:

        attempts, first_attempt_time = login_attempts[username]

        if current_time - first_attempt_time < LOCKOUT_TIME:

            if attempts >= MAX_LOGIN_ATTEMPTS:
                return "<h2>Too many failed login attempts. Try again later.</h2>", 429

        else:
            # Lockout period has expired
            del login_attempts[username]

    connection = get_db()

    query = """
        SELECT username, password_hash
        FROM users
        WHERE username = ?
    """

    result = connection.execute(
        query,
        (username,)
    ).fetchone()

    connection.close()

    if result:

        stored_hash = result[1]

        if check_password_hash(
            stored_hash,
            password
        ):

            # Successful login resets failed attempts
            if username in login_attempts:
                del login_attempts[username]

            # Create a login session
            session["username"] = username

            return "<h2>Login successful!</h2>"

    # Record failed login attempt
    if username not in login_attempts:
        login_attempts[username] = [1, current_time]
    else:
        login_attempts[username][0] += 1

    return "<h2>Invalid username or password.</h2>"


@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return "<h2>Please log in first.</h2>", 401

    username = session["username"]

    return f"""
    <h1>Secure Dashboard</h1>

    <h2>Welcome, {username}!</h2>

    <p>You are successfully logged in.</p>

    <a href="/logout">Logout</a>
    """

@app.route("/logout")
def logout():

    session.clear()

    return "<h2>You have been logged out successfully.</h2>"

@app.route("/comment")
def comment():

    comment_text = request.args.get(
        "comment",
        ""
    ).strip()

    if len(comment_text) > 500:
        return "<h2>Comment is too long.</h2>", 400

    # FIX 3: Jinja automatically escapes HTML
    page = """
    <h1>Comment</h1>

    <p>Your comment:</p>

    <div>
        {{ comment }}
    </div>

    <br>

    <a href="/">
        Go back
    </a>
    """

    return render_template_string(
        page,
        comment=comment_text
    )

@app.errorhandler(404)
def page_not_found(error):

    return "<h2>Page not found.</h2>", 404

if __name__ == "__main__":

    create_database()

    app.run(debug=False)