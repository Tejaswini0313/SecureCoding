import sys
import os

import pytest


# Allow Python to find secure_app.py
SECURE_VERSION_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "secure_version"
    )
)

sys.path.insert(0, SECURE_VERSION_PATH)

import secure_app
from secure_app import app


@pytest.fixture
def client(tmp_path, monkeypatch):

    # Create a completely fresh temporary database
    test_database = tmp_path / "test_users.db"

    # Make the application use the temporary database
    monkeypatch.setattr(
        secure_app,
        "DATABASE",
        str(test_database)
    )

    # Create the database tables
    secure_app.create_database()

    # Enable Flask testing mode
    app.config["TESTING"] = True

    # Clear login-attempt tracking before every test
    secure_app.login_attempts.clear()

    with app.test_client() as client:
        yield client


def get_csrf_token(client):

    response = client.get("/")

    assert response.status_code == 200

    html = response.data.decode()

    marker = 'name="csrf_token"'

    start = html.find(marker)

    assert start != -1

    value_marker = 'value="'

    value_start = html.find(
        value_marker,
        start
    ) + len(value_marker)

    value_end = html.find(
        '"',
        value_start
    )

    return html[value_start:value_end]


def test_home_page(client):

    response = client.get("/")

    assert response.status_code == 200


def test_normal_login(client):

    # Get a valid CSRF token
    csrf_token = get_csrf_token(client)

    # Create a test user
    register_response = client.post(
        "/register",
        data={
            "username": "pytest_user",
            "password": "Pytest@123",
            "csrf_token": csrf_token
        }
    )

    assert register_response.status_code == 200

    # Get a fresh CSRF token for the login request
    csrf_token = get_csrf_token(client)

    # Test login with the newly created user
    response = client.post(
        "/login",
        data={
            "username": "pytest_user",
            "password": "Pytest@123",
            "csrf_token": csrf_token
        }
    )

    assert response.status_code == 200
    assert b"Login successful" in response.data


def test_sql_injection_is_rejected(client):

    csrf_token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "username": "' OR '1'='1",
            "password": "anything",
            "csrf_token": csrf_token
        }
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_empty_login_is_rejected(client):

    csrf_token = get_csrf_token(client)

    response = client.post(
        "/login",
        data={
            "username": "",
            "password": "",
            "csrf_token": csrf_token
        }
    )

    assert response.status_code == 400


def test_xss_is_escaped(client):

    response = client.get(
        "/comment",
        query_string={
            "comment": '<script>alert("XSS")</script>'
        }
    )

    assert b"<script>" not in response.data


def test_long_comment_is_rejected(client):

    long_comment = "A" * 501

    response = client.get(
        "/comment",
        query_string={
            "comment": long_comment
        }
    )

    assert response.status_code == 400


def test_security_headers(client):

    response = client.get("/")

    assert response.headers[
        "X-Content-Type-Options"
    ] == "nosniff"

    assert response.headers[
        "X-Frame-Options"
    ] == "DENY"

    assert "Content-Security-Policy" in response.headers


def test_unknown_page_returns_404(client):

    response = client.get("/this-page-does-not-exist")

    assert response.status_code == 404


def test_dashboard_xss_is_escaped(client):

    with client.session_transaction() as session:
        session["username"] = "<script>alert('XSS')</script>"

    response = client.get("/dashboard")

    assert response.status_code == 200

    assert b"<script>alert('XSS')</script>" not in response.data

    assert b"&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;" in response.data

def test_csrf_protection(client):

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "Test@12345"
        }
    )

    assert response.status_code == 400
    assert b"CSRF token is missing" in response.data

def test_session_cookie_security(client):

    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_SECURE"] is False