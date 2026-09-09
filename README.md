# Secure Coding Review

---

## 1. Introduction

This project demonstrates the importance of secure coding practices using a small Python Flask web application.

The application was initially developed with intentionally vulnerable code to demonstrate common web security weaknesses. The vulnerable version was then reviewed, security risks were identified, and a secure version was developed to mitigate the identified vulnerabilities.

The project also includes automated security tests using `pytest` to verify that the security improvements work correctly.

---

## 2. Objectives

The main objectives of this project are:

* Identify common vulnerabilities in a Flask web application
* Understand how insecure code can be exploited
* Implement secure coding practices
* Protect user authentication
* Prevent SQL injection
* Prevent Cross-Site Scripting (XSS)
* Protect against Cross-Site Request Forgery (CSRF)
* Secure user session cookies
* Validate user input
* Implement security-related HTTP headers
* Implement login attempt protection
* Create automated security tests
* Compare vulnerable and secure implementations

---

## 3. Technologies Used

* Python 3
* Flask
* Flask-WTF
* SQLite
* Werkzeug
* python-dotenv
* HTML
* pytest
* Visual Studio Code
* Git and GitHub

---

## 4. Project Structure

The project is organized into separate folders for the vulnerable application, secure application, and security tests.

```text
SecureCoding/

│
├── secure_version/
│   └── secure_app.py
│
├── vulnerable_version/
│   └── vulnerable_app.py
│
├── tests/
│   └── test_security.py
│
├── .gitignore
├── README.md
├── SECURITY_REVIEW.md
└── requirements.txt
```

### File Description

* `secure_version/secure_app.py` — secure Flask application
* `vulnerable_version/vulnerable_app.py` — intentionally vulnerable Flask application
* `tests/test_security.py` — automated security tests
* `README.md` — project documentation
* `SECURITY_REVIEW.md` — detailed security analysis
* `requirements.txt` — required Python packages
* `.gitignore` — prevents sensitive and unnecessary local files from being uploaded

The local SQLite database files, virtual environment, cache files, and `.env` files are intentionally excluded from GitHub using `.gitignore`.

---

# 5. Vulnerability 1 — SQL Injection

## Vulnerable Code

The vulnerable application constructed SQL queries using user-controlled input.

This is dangerous because an attacker may provide specially crafted input that changes the intended SQL query.

For example, directly inserting user input into an SQL statement can allow an attacker to manipulate the query.

## Security Risk

SQL injection can potentially allow an attacker to:

* Bypass authentication
* Access unauthorized information
* Modify database operations
* Manipulate application data

## Secure Fix

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
```

Using placeholders ensures that user input is treated as data rather than executable SQL.

---

# 6. Vulnerability 2 — Cross-Site Scripting (XSS)

## Vulnerable Behavior

The vulnerable application could allow user-controlled input to be rendered without sufficient escaping.

An attacker could attempt to submit JavaScript such as:

```html
<script>alert('XSS')</script>
```

## Security Risk

Successful XSS attacks can allow malicious scripts to execute in another user's browser.

Potential consequences include:

* Session-related attacks
* Malicious page modifications
* User redirection
* Theft of information accessible to client-side scripts

## Secure Fix

The secure application uses Jinja template escaping when displaying user-controlled input.

Example:

```html
{{ comment }}
```

Jinja automatically escapes HTML content, preventing submitted JavaScript from being interpreted as executable HTML or JavaScript.

The dashboard also uses safe template rendering for the username.

---

# 7. Password Security

The secure application does not store passwords as plain text.

Passwords are protected using Werkzeug password hashing functions:

```python
generate_password_hash()
```

Passwords are verified using:

```python
check_password_hash()
```

This provides significantly better protection than storing raw passwords in the database.

Password hashing helps protect user credentials if the database is compromised.

---

# 8. Input Validation

The secure application validates user input before processing it.

Security checks include:

* Empty username validation
* Empty password validation
* Username length validation
* Password length validation
* Minimum password length requirement
* Comment length validation
* Safe handling of user-controlled input

Input validation reduces unexpected behavior and helps prevent abuse of application functionality.

It also ensures that invalid or excessively large input is rejected appropriately.

---

# 9. Login Attempt Protection

The secure application implements temporary login lockout protection.

The application limits repeated failed login attempts using:

```python
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 60
```

After multiple failed attempts, the username is temporarily blocked from further login attempts.

This helps reduce the risk of simple brute-force password attacks.

Successful authentication resets the failed-attempt counter.

---

# 10. Cross-Site Request Forgery (CSRF) Protection

The secure application uses Flask-WTF to provide CSRF protection.

CSRF protection is enabled using:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

The registration and login forms include a CSRF token:

```html
<input type="hidden"
       name="csrf_token"
       value="{{ csrf_token() }}">
```

The server validates this token before processing protected POST requests.

Requests without a valid CSRF token are rejected.

This helps prevent attackers from forcing authenticated users to submit unwanted requests.

---

# 11. Secure Session Cookies

The application uses secure session-cookie configuration.

The following settings are implemented:

```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
```

### HTTPOnly

`HTTPOnly=True` prevents client-side JavaScript from directly accessing the session cookie.

### SameSite

`SameSite="Lax"` provides additional protection against cross-site requests.

### Secure

`SESSION_COOKIE_SECURE` is currently set to `False` because the application is being tested locally over HTTP.

For an HTTPS production deployment, it should be changed to:

```python
app.config["SESSION_COOKIE_SECURE"] = True
```

---

# 12. Security Headers

The secure application implements security-related HTTP response headers.

The application includes:

### X-Content-Type-Options

```text
nosniff
```

Helps prevent browsers from MIME-sniffing responses.

### X-Frame-Options

```text
DENY
```

Prevents the application from being embedded in frames.

### Content-Security-Policy

The application uses a Content Security Policy that restricts the sources from which browser content can be loaded.

Example:

```text
default-src 'self';
script-src 'self';
object-src 'none';
frame-ancestors 'none';
```

These headers provide an additional layer of browser-side protection alongside secure application code.

---

# 13. Automated Security Testing

The project includes automated security tests using `pytest`.

The current test suite checks:

* Home page availability
* Normal login
* SQL injection rejection
* Empty login rejection
* XSS escaping
* Long comment rejection
* Security headers
* Unknown page handling
* Dashboard XSS protection
* CSRF protection
* Session-cookie security configuration

Run the tests using:

```powershell
pytest -v
```

## Test Result

The complete security test suite currently passes successfully:

```text
11 passed
```

This confirms that all eleven automated security tests passed successfully.

---

# 14. Security Testing Performed

The secure application was manually and automatically tested against common security attack inputs.

## SQL Injection Test

Example malicious input:

```text
' OR '1'='1
```

Expected result:

```text
Invalid username or password
```

The authentication bypass was rejected.

## XSS Test

Example malicious input:

```html
<script>alert('XSS Test')</script>
```

Expected result:

The script is safely escaped rather than executed.

## Dashboard XSS Test

A malicious username containing HTML/JavaScript was tested against the dashboard.

Expected result:

The malicious content is HTML-escaped and is not executed as JavaScript.

## CSRF Test

A POST request without a CSRF token was tested.

Expected result:

```text
400 Bad Request
```

The request is rejected because the CSRF token is missing.

## Invalid Login Test

Incorrect credentials are rejected instead of allowing unauthorized access.

## Long Input Test

Excessively long comments are rejected according to the application's validation rules.

## Security Header Test

The secure application returns the expected security-related HTTP headers.

## Session Security Test

The automated test suite verifies the configured session-cookie security settings.

---

# 15. Vulnerable vs Secure Version

| Security Area    | Vulnerable Version         | Secure Version                   |
| ---------------- | -------------------------- | -------------------------------- |
| SQL queries      | Unsafe user input handling | Parameterized queries            |
| Passwords        | Insecure handling          | Password hashing                 |
| XSS              | Unsafe output handling     | Jinja HTML escaping              |
| Input validation | Limited                    | Implemented                      |
| Login protection | Limited                    | Failed-attempt lockout           |
| CSRF             | Not implemented            | Flask-WTF CSRF protection        |
| Session cookies  | Default configuration      | HTTPOnly and SameSite configured |
| Security headers | Missing or limited         | Implemented                      |
| Automated tests  | Not available              | 11 security tests                |
| Error handling   | Less secure                | Improved validation and handling |

The comparison demonstrates how secure coding practices improve the security of the application.

---

# 16. Security Review

A detailed security analysis is available in:

`SECURITY_REVIEW.md`

The security review explains:

* Identified vulnerabilities
* Security risks
* Vulnerable coding practices
* Recommended security controls
* Secure implementation techniques
* Testing and verification

The document provides additional details beyond the summary presented in this README.

---

# 17. Running the Secure Application

## Step 1 — Create the Virtual Environment

From the project directory, run:

```powershell
python -m venv venv
```

## Step 2 — Activate the Virtual Environment

On Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

## Step 3 — Install Dependencies

Install the required packages:

```powershell
pip install -r requirements.txt
```

## Step 4 — Run Security Tests

Run:

```powershell
pytest -v
```

The expected result is:

```text
11 passed
```

## Step 5 — Start the Secure Application

From the project root directory, run:

```powershell
python secure_version\secure_app.py
```

The application will run at:

```text
http://127.0.0.1:5000
```

Open this address in a web browser.

---

# 18. GitHub Repository

The complete project is available on GitHub:

https://github.com/Tejaswini0313/SecureCoding

The repository contains:

* Vulnerable application
* Secure application
* Automated security tests
* Security review documentation
* Project README
* Python dependency information

Sensitive local files such as the virtual environment, database files, cache files, and `.env` files are excluded using `.gitignore`.

---

# 19. Conclusion

This project demonstrates how insecure programming practices can introduce vulnerabilities into web applications and how secure coding techniques can reduce those risks.

The secure version improves the application's security through:

* Parameterized SQL queries
* Password hashing
* XSS protection
* Input validation
* Login attempt protection
* CSRF protection
* Secure session-cookie configuration
* Security headers
* Automated security testing

The final implementation successfully passed all **11 automated security tests**.

This project demonstrates the importance of identifying vulnerabilities during code review and applying appropriate secure coding practices to protect web applications and user data.
