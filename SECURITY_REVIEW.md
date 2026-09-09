# Security Coding Review Report

## 1. Executive Summary

This project presents a secure coding review of a small Python Flask web application.

An intentionally vulnerable version of the application was created to demonstrate common web security weaknesses. The vulnerable version was reviewed, security risks were identified, and a separate secure version was developed to address the identified vulnerabilities.

The primary vulnerabilities identified during the review were:

1. SQL Injection
2. Cross-Site Scripting (XSS)
3. Plain-Text Password Storage

Additional security weaknesses and protection requirements were addressed through:

* Server-side input validation
* Parameterized SQL queries
* Password hashing
* HTML output escaping
* CSRF protection
* Login attempt protection
* Secure session-cookie configuration
* Security-related HTTP headers
* Safe error handling
* Production-safe debug configuration
* Automated security testing

The secure implementation was verified using an automated `pytest` security test suite.

### Final Test Result

```text
11 passed
```

All 11 automated security tests passed successfully.

---

# 2. Scope

The assessment covered the following components:

* User registration
* User login
* Authentication handling
* Session management
* User input handling
* Database interaction
* Comment functionality
* Password storage
* Dashboard functionality
* HTTP security headers
* CSRF protection
* Login attempt protection
* Error handling
* Automated security tests

Testing was performed against the local Flask application.

No external systems or third-party applications were tested.

---

# 3. Technology Stack

| Component                 | Technology         |
| ------------------------- | ------------------ |
| Programming Language      | Python 3           |
| Web Framework             | Flask              |
| Database                  | SQLite             |
| Security Library          | Werkzeug           |
| CSRF Protection           | Flask-WTF          |
| Environment Configuration | python-dotenv      |
| Testing Framework         | pytest             |
| Development Environment   | Visual Studio Code |
| Version Control           | Git                |
| Repository                | GitHub             |

---

# 4. Security Findings Summary

| Finding                     | Vulnerable Version    | Secure Version                  | Status      |
| --------------------------- | --------------------- | ------------------------------- | ----------- |
| SQL Injection               | Present               | Parameterized queries           | Fixed       |
| Cross-Site Scripting        | Present               | HTML escaping                   | Fixed       |
| Plain-Text Password Storage | Present               | Password hashing                | Fixed       |
| Input Validation            | Limited               | Server-side validation          | Improved    |
| Brute-Force Protection      | Limited/Absent        | Login attempt lockout           | Implemented |
| CSRF                        | Not protected         | Flask-WTF CSRF protection       | Implemented |
| Session Cookies             | Default configuration | HTTPOnly/SameSite configuration | Improved    |
| Security Headers            | Missing/Limited       | CSP, X-Frame-Options, nosniff   | Implemented |
| Error Handling              | Basic                 | Controlled responses            | Improved    |
| Automated Testing           | Limited               | 11 security tests               | Implemented |

---

# 5. Vulnerability 1 — SQL Injection

## Severity

**High**

## Description

The vulnerable application constructed SQL queries using user-controlled input.

When untrusted input is directly concatenated into an SQL statement, an attacker may manipulate the structure of the query.

For example, the vulnerable implementation followed the unsafe pattern:

```python
query = (
    "SELECT * FROM users "
    "WHERE username = '" + username +
    "' AND password = '" + password + "'"
)
```

This allows user input to become part of the SQL syntax.

Parameterized queries are the recommended defense because they separate SQL code from user-supplied data.

## Security Impact

A successful SQL injection attack could potentially allow an attacker to:

* Bypass authentication
* Access unauthorized information
* Modify application data
* Manipulate database operations
* Potentially affect other database functionality

## Secure Fix

The secure application uses parameterized SQL queries:

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

The username is passed separately from the SQL statement.

This ensures that user input is treated as data rather than executable SQL.

## Verification

The automated test:

```text
test_sql_injection_is_rejected
```

successfully verifies that a SQL injection-style login attempt does not bypass authentication.

**Status: Fixed**

---

# 6. Vulnerability 2 — Cross-Site Scripting (XSS)

## Severity

**High**

## Description

The vulnerable application could render user-controlled input without sufficient HTML escaping.

An attacker could attempt to submit malicious HTML or JavaScript such as:

```html
<script>alert('XSS Test')</script>
```

If this input were rendered as executable HTML, the attacker's JavaScript could execute in a victim's browser.

## Security Impact

Successful XSS attacks can potentially allow:

* Malicious script execution
* Unauthorized page modification
* User redirection
* Theft of information accessible to client-side scripts
* Session-related attacks

## Secure Fix

The secure application uses Jinja template escaping when displaying user-controlled content.

Example:

```html
{{ comment }}
```

Jinja automatically escapes HTML characters in the rendered value.

The application also safely renders the username on the dashboard.

## Verification

The following automated tests verify XSS protection:

```text
test_xss_is_escaped
test_dashboard_xss_is_escaped
```

The malicious HTML is escaped instead of being executed.

**Status: Fixed**

---

# 7. Vulnerability 3 — Plain-Text Password Storage

## Severity

**High**

## Description

The vulnerable implementation stored passwords in an insecure form.

Storing passwords as plain text is dangerous because anyone who obtains access to the database could directly read the users' passwords.

## Security Impact

A compromised database containing plain-text passwords could expose user credentials.

Users may also reuse passwords on other services, increasing the impact of a credential compromise.

## Secure Fix

The secure application uses Werkzeug's password hashing functions.

Password registration uses:

```python
generate_password_hash(password)
```

Password verification uses:

```python
check_password_hash(
    stored_hash,
    password
)
```

The database stores the password hash instead of the original password.

## Security Benefit

Password hashing makes it significantly more difficult to recover the original password from the stored database value.

**Status: Fixed**

---

# 8. Input Validation

## Description

The secure application performs server-side validation before processing user input.

Validation controls include:

* Empty username rejection
* Empty password rejection
* Username length restriction
* Password length restriction
* Minimum password length requirement
* Comment length restriction
* Safe handling of user-controlled values

## Implemented Limits

Username:

```text
Maximum: 50 characters
```

Password:

```text
Minimum: 8 characters
Maximum: 128 characters
```

Comment:

```text
Maximum: 500 characters
```

## Security Benefit

Server-side validation helps prevent unexpected application behavior and limits excessive or malformed input.

Input validation should be considered an additional security layer rather than a replacement for parameterized queries or contextual output encoding.

**Status: Implemented**

---

# 9. Login Attempt Protection

## Description

The secure application implements temporary protection against repeated failed login attempts.

The application uses:

```python
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME = 60
```

After five failed login attempts for a username, further attempts are temporarily rejected during the lockout period.

## Security Benefit

This reduces the effectiveness of simple automated brute-force attempts against user accounts.

A successful login also resets the failed-attempt counter.

Account protection and lockout mechanisms are recognized as important authentication security controls.

**Status: Implemented**

---

# 10. Cross-Site Request Forgery (CSRF) Protection

## Severity

**Medium**

## Description

Cross-Site Request Forgery occurs when an attacker attempts to cause a user's browser to submit an unwanted request to an application where the user is authenticated.

The secure application uses Flask-WTF CSRF protection.

The application includes:

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

Protected forms include a CSRF token.

Example:

```html
<input type="hidden"
       name="csrf_token"
       value="{{ csrf_token() }}">
```

The server validates the token before accepting protected POST requests.

## Security Verification

The automated test:

```text
test_csrf_protection
```

submits a request without a CSRF token.

The request is rejected with:

```text
400 Bad Request
```

This verifies that CSRF protection is active.

**Status: Implemented**

---

# 11. Session Security

## Description

The application uses Flask's built-in session mechanism to maintain authenticated user state.

The secure version configures session cookies with additional security controls:

```python
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
```

## HTTPOnly

The `HTTPOnly` attribute prevents client-side JavaScript from directly reading the session cookie.

This helps reduce the impact of certain XSS-based cookie theft scenarios.

## SameSite

The `SameSite=Lax` setting provides an additional defense against unwanted cross-site cookie transmission.

SameSite is considered defense in depth and does not replace CSRF tokens.

## Secure

The application currently uses:

```python
SESSION_COOKIE_SECURE = False
```

because the application is being tested locally using:

```text
http://127.0.0.1:5000
```

For a production HTTPS deployment, this should be changed to:

```python
SESSION_COOKIE_SECURE = True
```

## Verification

The automated test:

```text
test_session_cookie_security
```

verifies the configured session-cookie security settings.

**Status: Implemented for local development**

---

# 12. Security Headers

## Description

The secure application adds security-related HTTP response headers.

### X-Content-Type-Options

```text
nosniff
```

Helps prevent browsers from MIME-sniffing responses.

### X-Frame-Options

```text
DENY
```

Prevents the application from being embedded inside frames.

### Content-Security-Policy

The application implements:

```text
default-src 'self';
script-src 'self';
object-src 'none';
frame-ancestors 'none';
```

This restricts the sources from which browser content can be loaded and prevents framing of the application.

## Verification

The automated test:

```text
test_security_headers
```

verifies the presence of the required security headers.

**Status: Implemented**

---

# 13. Secure Error Handling

The secure application provides controlled responses for invalid requests.

For example, unknown routes return:

```text
Page not found.
```

with HTTP status:

```text
404
```

The application also returns appropriate status codes for invalid input and security-related failures.

Examples include:

```text
400 Bad Request
401 Unauthorized
404 Not Found
409 Conflict
429 Too Many Requests
```

The application does not run Flask in debug mode:

```python
app.run(debug=False)
```

This prevents the interactive Flask debugger from being enabled in the application configuration.

**Status: Implemented**

---

# 14. Automated Security Testing

The project includes an automated security test suite using `pytest`.

The current test suite contains **11 tests**.

## Test Coverage

### 1. Home Page

```text
test_home_page
```

Verifies that the application home page is available.

### 2. Normal Login

```text
test_normal_login
```

Verifies that valid credentials can authenticate successfully.

### 3. SQL Injection

```text
test_sql_injection_is_rejected
```

Verifies that SQL injection-style input cannot bypass authentication.

### 4. Empty Login

```text
test_empty_login_is_rejected
```

Verifies that empty credentials are rejected.

### 5. XSS Protection

```text
test_xss_is_escaped
```

Verifies that malicious HTML is escaped.

### 6. Long Comment

```text
test_long_comment_is_rejected
```

Verifies that comments exceeding the configured limit are rejected.

### 7. Security Headers

```text
test_security_headers
```

Verifies the required HTTP security headers.

### 8. Unknown Page

```text
test_unknown_page_returns_404
```

Verifies correct handling of unknown routes.

### 9. Dashboard XSS

```text
test_dashboard_xss_is_escaped
```

Verifies that malicious content stored in the session username is safely escaped on the dashboard.

### 10. CSRF Protection

```text
test_csrf_protection
```

Verifies that protected POST requests without a CSRF token are rejected.

### 11. Session Cookie Security

```text
test_session_cookie_security
```

Verifies the configured HTTPOnly, SameSite, and Secure session-cookie settings.

---

# 15. Final Test Result

The complete automated security test suite was executed using:

```powershell
pytest -v
```

Final result:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0
collected 11 items

tests/test_security.py::test_home_page PASSED
tests/test_security.py::test_normal_login PASSED
tests/test_security.py::test_sql_injection_is_rejected PASSED
tests/test_security.py::test_empty_login_is_rejected PASSED
tests/test_security.py::test_xss_is_escaped PASSED
tests/test_security.py::test_long_comment_is_rejected PASSED
tests/test_security.py::test_security_headers PASSED
tests/test_security.py::test_unknown_page_returns_404 PASSED
tests/test_security.py::test_dashboard_xss_is_escaped PASSED
tests/test_security.py::test_csrf_protection PASSED
tests/test_security.py::test_session_cookie_security PASSED

============================= 11 passed =============================
```

### Result

**11/11 security tests passed successfully.**

This provides automated evidence that the implemented security controls are functioning as expected for the tested scenarios.

---

# 16. Vulnerable vs Secure Implementation

| Security Area     | Vulnerable Implementation | Secure Implementation               |
| ----------------- | ------------------------- | ----------------------------------- |
| SQL queries       | String concatenation      | Parameterized queries               |
| Authentication    | Unsafe query construction | Parameterized authentication query  |
| Passwords         | Plain-text storage        | Password hashing                    |
| XSS               | Unsafe output handling    | Jinja HTML escaping                 |
| Input validation  | Limited                   | Server-side validation              |
| Login attempts    | Limited protection        | Temporary lockout                   |
| CSRF              | Not implemented           | Flask-WTF CSRF protection           |
| Session cookies   | Default settings          | HTTPOnly and SameSite configuration |
| Security headers  | Missing/Limited           | CSP, X-Frame-Options, nosniff       |
| Error handling    | Basic                     | Controlled HTTP responses           |
| Debug mode        | Unsafe for production     | Disabled                            |
| Automated testing | Limited                   | 11 security tests                   |

---

# 17. Security Improvements Implemented

The secure version introduces multiple layers of defense.

### Database Security

* Parameterized SQL queries
* No direct SQL string concatenation
* SQLite database isolation for tests

### Authentication Security

* Password hashing
* Password verification using secure hashing functions
* Username and password validation
* Login attempt protection

### Web Security

* XSS protection through HTML escaping
* CSRF protection
* Content Security Policy
* X-Frame-Options
* X-Content-Type-Options

### Session Security

* HTTPOnly session cookies
* SameSite cookie configuration
* Secure-cookie configuration documented for HTTPS deployment
* Session clearing during logout

### Testing

* Automated security test suite
* SQL injection test
* XSS tests
* CSRF test
* Session security test
* Security header test
* Input validation tests

---

# 18. Limitations and Future Improvements

Although the application now implements several important security controls, it is still a small educational Flask application and should not be considered production-ready without further hardening.

Potential future improvements include:

* HTTPS/TLS deployment
* Enabling `SESSION_COOKIE_SECURE=True` in production
* Stronger password policy
* Multi-factor authentication
* Persistent rate limiting instead of in-memory login tracking
* Account recovery security
* Security event logging and monitoring
* Database access controls
* Automated dependency vulnerability scanning
* More comprehensive authorization controls
* Production WSGI server deployment
* Additional automated security tests
* HSTS configuration for HTTPS deployments

The in-memory login-attempt dictionary is particularly suitable for this educational project but would need a shared/persistent mechanism in a multi-process production deployment.

---

# 19. Security Testing Methodology

The security review used a combination of:

### Static Code Review

The application source code was reviewed to identify insecure coding patterns such as:

* SQL string concatenation
* Plain-text password storage
* Unsafe output rendering
* Missing security controls

### Manual Security Testing

The application was manually tested using malicious and invalid inputs, including:

```text
' OR '1'='1
```

and:

```html
<script>alert('XSS Test')</script>
```

### Automated Testing

`pytest` was used to repeatedly verify security controls and prevent regressions.

The final test suite contains:

```text
11 automated tests
```

with:

```text
11 passed
```

---

# 20. Conclusion

This project demonstrates how insecure programming practices can introduce vulnerabilities into web applications and how secure coding techniques can reduce those risks.

The vulnerable version demonstrated security weaknesses including:

* SQL Injection
* Cross-Site Scripting
* Plain-text password storage

The secure version addressed these issues and introduced additional security controls including:

* Parameterized SQL queries
* Password hashing
* Input validation
* XSS protection
* Login attempt protection
* CSRF protection
* Secure session-cookie configuration
* Security headers
* Controlled error handling
* Automated security testing

The final implementation successfully passed all:

```text
11 / 11 automated security tests
```

This project demonstrates the importance of secure code review, defense in depth, automated testing, and secure development practices when building web applications.

The project is intended as an educational secure-coding demonstration and provides a foundation for further security hardening before production deployment.
