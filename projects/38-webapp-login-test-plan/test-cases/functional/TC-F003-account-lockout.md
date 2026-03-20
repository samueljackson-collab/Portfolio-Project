# TC-F003: Account Lockout After 5 Failed Attempts

| Field | Value |
|-------|-------|
| **Test Case ID** | TC-F003 |
| **Test Case Name** | Account Lockout After 5 Failed Attempts |
| **Module** | Authentication / Rate Limiting |
| **Priority** | P1 — Critical |
| **Category** | Functional |
| **Requirement** | REQ-F003 |
| **Author** | Sam Jackson |
| **Date Created** | 2026-01-15 |
| **Status** | Pass |

---

## Objective

Verify that the application enforces account lockout after 5 consecutive
failed login attempts from the same IP address, returning HTTP 429 and
blocking further attempts.

---

## Preconditions

1. Flask application is running on `http://localhost:5001`
2. Login attempt counter for the test IP is at 0 (fresh state)
3. No active session exists for the test client

---

## Test Data

| Scenario | Username | Password | Attempt # | Expected Status |
|----------|----------|----------|-----------|-----------------|
| Failed attempt 1 | `admin` | `wrong` | 1 | 401 |
| Failed attempt 2 | `admin` | `wrong` | 2 | 401 |
| Failed attempt 3 | `admin` | `wrong` | 3 | 401 |
| Failed attempt 4 | `admin` | `wrong` | 4 | 401 |
| Failed attempt 5 | `admin` | `wrong` | 5 | 401 |
| Failed attempt 6 (lockout) | `admin` | `wrong` | 6 | 429 |
| Failed attempt 7 (still locked) | `admin` | `correct` | 7 | 429 |

---

## Test Steps

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Send 5 `POST /login` requests with wrong password for `admin` | All return 401 |
| 2 | Send 6th `POST /login` with wrong password | Returns 429 Too Many Requests |
| 3 | Check response body for lockout message | Contains "Account locked" or "Too many" |
| 4 | Send 7th `POST /login` with CORRECT password | Still returns 429 (IP is locked) |
| 5 | Verify lockout message in response | Same lockout error |

---

## Expected Result (Step 2+)

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
    "error": "Account locked after too many attempts"
}
```

---

## Actual Result

```
Attempts 1-5: 401 Unauthorized
Attempt 6:    429 Too Many Requests
Body: {"error": "Account locked after too many attempts"}
```

**Result: PASS**

---

## Counter Reset Behavior

The lockout counter resets to 0 on a successful authentication (when
the IP is not yet locked). This allows legitimate users to recover if
they accidentally mistype a password.

---

## Security Notes

This implementation uses IP-based rate limiting. Production environments
should consider:
- Username-based lockout (in addition to IP)
- CAPTCHA after N failures
- Exponential backoff
- Alerting on repeated lockout events
- Redis-backed counter (current in-memory counter resets on restart)

---

## Automated Test

```python
def test_account_lockout(client):
    for _ in range(6):
        client.post("/login", json={"username": "baduser", "password": "wrong"})
    resp = client.post("/login", json={"username": "baduser", "password": "wrong"})
    assert resp.status_code == 429
```
