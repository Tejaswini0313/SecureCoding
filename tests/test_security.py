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


def test_home_page(client):

    response = client.get("/")

    assert response.status_code == 200


def test_normal_login(client):

    # Create a test user
    register_response = client.post(
        "/register",
        data={
            "username": "pytest_user",
            "password": "Pytest@123"
        }
    )

    assert register_response.status_code == 200

    # Test login with the newly created user
    response = client.post(
        "/login",
        data={
            "username": "pytest_user",
            "password": "Pytest@123"
        }
    )

    assert response.status_code == 200
    assert b"Login successful" in response.data


def test_sql_injection_is_rejected(client):

    response = client.post(
        "/login",
        data={
            "username": "' OR '1'='1",
            "password": "anything"
        }
    )

    assert b"Invalid username or password" in response.data


def test_empty_login_is_rejected(client):

    response = client.post(
        "/login",
        data={
            "username": "",
            "password": ""
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