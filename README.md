# Task 3 — Secure Coding Review

## 1. Introduction

This project demonstrates the importance of secure coding practices
using a small Python Flask web application.

The application was first created intentionally with common security
vulnerabilities. The vulnerable version was then reviewed and a secure
version was developed to mitigate the identified vulnerabilities.

---

## 2. Technologies Used

- Python
- Flask
- SQLite
- Werkzeug
- HTML
- Visual Studio Code

---

## 3. Project Structure

The project contains:

- vulnerable_app.py — intentionally vulnerable application
- secure_app.py — secure version of the application
- users.db — database used by the vulnerable application
- secure_users.db — database used by the secure application
- requirements.txt — required Python packages
- README.md — project documentation

---

# 4. Vulnerability 1 — SQL Injection

## Vulnerable Code

The vulnerable application constructed an SQL query by directly
concatenating user input with the SQL statement.

This is dangerous because specially crafted input can change the
meaning of the SQL query.

## Security Risk

An attacker could potentially:

- bypass authentication
- access unauthorized data
- manipulate database queries

## Fix

The secure application uses parameterized SQL queries.

Example:

```python
query = """
    SELECT username, password_hash
    FROM users
    WHERE username = ?
"""

result = connection.execute(
    query,
    (username,)
).fetchone()