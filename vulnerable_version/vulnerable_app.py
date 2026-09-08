from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

DATABASE = "users.db"


def get_db():
    connection = sqlite3.connect(DATABASE)
    return connection


def create_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    # Demo accounts
    connection.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("admin", "admin123")
    )

    connection.execute(
        "INSERT INTO users (username, password) VALUES (?, ?)",
        ("student", "student123")
    )

    connection.commit()
    connection.close()


@app.route("/")
def home():
    return """
    <h1>Secure Coding Review</h1>

    <h2>Login</h2>

    <form action="/login" method="POST">

        Username:
        <input type="text" name="username">

        <br><br>

        Password:
        <input type="password" name="password">

        <br><br>

        <button type="submit">Login</button>

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


@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    connection = get_db()

    # INTENTIONALLY VULNERABLE: SQL Injection
    query = (
        "SELECT * FROM users "
        "WHERE username = '" + username +
        "' AND password = '" + password + "'"
    )

    result = connection.execute(query).fetchone()

    connection.close()

    if result:
        return "<h2>Login successful!</h2>"

    return "<h2>Invalid username or password.</h2>"


@app.route("/comment")
def comment():

    comment_text = request.args.get("comment", "")

    # INTENTIONALLY VULNERABLE: XSS
    page = """
    <h1>Comment</h1>

    <p>Your comment:</p>

    <div>
        """ + comment_text + """
    </div>

    <br>

    <a href="/">Go back</a>
    """

    return render_template_string(page)


@app.route("/password")
def password():

    # INTENTIONALLY VULNERABLE:
    # Passwords are stored as plain text.

    connection = get_db()

    users = connection.execute(
        "SELECT username, password FROM users"
    ).fetchall()

    connection.close()

    result = "<h1>User Database</h1>"

    for username, password in users:

        result += (
            "<p>Username: "
            + username
            + " | Password: "
            + password
            + "</p>"
        )

    return result


if __name__ == "__main__":

    create_database()

    app.run(debug=True)