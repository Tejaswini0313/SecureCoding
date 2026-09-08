# Security Coding Review Report

## 1. Executive Summary

This project presents a secure coding review of a small Python Flask
web application.

An intentionally vulnerable version of the application was created
to identify common security weaknesses. A separate secure version
was then developed to address the identified issues.

The review identified three primary vulnerabilities:

1. SQL Injection
2. Cross-Site Scripting (XSS)
3. Plain-Text Password Storage

Additional security controls were implemented, including:

- Input validation
- Parameterized database queries
- Password hashing
- HTML output escaping
- Security headers
- Safe error handling
- Automated security testing
- Production-safe debug configuration

All automated security tests passed successfully.

---

# 2. Scope

The assessment covered the following components:

- User login functionality
- User input handling
- Database interaction
- Comment functionality
- Password storage
- HTTP security headers
- Error handling

Testing was performed against the local development application.

No external systems or third-party applications were tested.

---

# 3. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| Web Framework | Flask |
| Database | SQLite |
| Security Library | Werkzeug |
| Testing Framework | Pytest |
| Development Environment | Visual Studio Code |

---

# 4. Security Findings

## 4.1 SQL Injection

### Severity

High

### Description

The vulnerable application constructed SQL queries by directly
concatenating user-controlled input with the SQL statement.

### Vulnerable Pattern

```python
query = (
    "SELECT * FROM users "
    "WHERE username = '" + username +
    "' AND password = '" + password + "'"
)