# TC-F001: Valid Login — Admin User

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-F001 |
| **Test Case Name** | Valid Login — Admin User |
| **Module** | Authentication / Login |
| **Priority** | P1 — Critical |
| **Category** | Functional |
| **Requirement** | REQ-F001 |
| **Author** | Sam Jackson |
| **Date Created** | 2026-01-15 |
| **Last Updated** | 2026-01-15 |
| **Status** | Pass |

---

## Objective

Verify that a registered user with valid credentials can authenticate
successfully and receive a session token.

---

## Preconditions

1. Flask application is running on `http://localhost:5001`
2. `GET /health` returns `{"status": "healthy"}` (200 OK)
3. Admin user `admin` exists in the application user store with password `admin123!`
4. No active session exists for the test client
5. Login attempt counter for the test IP is 0 (not approaching lockout)

---

## Test Data

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123!` |
| Content-Type | `application/json` |

---

## Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send `POST /login` with body `{"username": "admin", "password": "admin123!"}` and `Content-Type: application/json` | Request sent without error |
| 2 | Check response HTTP status code | Status code is `200 OK` |
| 3 | Parse response JSON body | Body is valid JSON |
| 4 | Check `message` field in response | Value is `"Login successful"` |
| 5 | Check `user` field in response | Value is `"admin"` |
| 6 | Check response headers for `Set-Cookie` | Session cookie is present |
| 7 | Send `GET /profile` using the session cookie from step 6 | Profile returns 200 with user data |

---

## Expected Result

```http
HTTP/1.1 200 OK
Content-Type: application/json
Set-Cookie: session=<session-token>; HttpOnly; Path=/

{
    "message": "Login successful",
    "user": "admin"
}
```

---

## Actual Result

```
Status: 200 OK
Body: {"message": "Login successful", "user": "admin"}
Session cookie: Set
```

**Result: PASS**

---

## Automated Test

This test case is automated in `tests/test_login_app.py`:

```python
def test_valid_login(client):
    resp = client.post("/login", json={"username": "admin", "password": "admin123!"})
    assert resp.status_code == 200
    assert resp.json["user"] == "admin"
```

---

## Post-conditions

- Session is active for the admin user
- Login attempt counter reset to 0 for the test IP
- User can access protected routes like `/profile`

---

## Notes

- Password `admin123!` is used only in this test/demo application
- In production, passwords must be hashed with bcrypt or argon2id
- The SHA-256 comparison in this demo app is sufficient for test purposes only
