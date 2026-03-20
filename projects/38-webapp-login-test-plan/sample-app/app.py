from flask import Flask, request, jsonify, session
import hashlib, os, time
from functools import wraps
from collections import defaultdict

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-not-for-production")

# User database (hashed passwords)
USERS = {
    "admin":    hashlib.sha256("Admin@1234!".encode()).hexdigest(),
    "user1":    hashlib.sha256("User@5678!".encode()).hexdigest(),
    "testuser": hashlib.sha256("Test@9999!".encode()).hexdigest(),
}

# Rate limiting tracker: {ip: [timestamp, ...]}
LOGIN_ATTEMPTS = defaultdict(list)
MAX_ATTEMPTS = 5
LOCKOUT_WINDOW = 300  # 5 minutes


def is_rate_limited(ip: str) -> bool:
    now = time.time()
    # Clean old attempts outside window
    LOGIN_ATTEMPTS[ip] = [t for t in LOGIN_ATTEMPTS[ip] if now - t < LOCKOUT_WINDOW]
    return len(LOGIN_ATTEMPTS[ip]) >= MAX_ATTEMPTS


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/health")
def health():
    return jsonify({"status": "healthy", "version": "1.0.0"}), 200


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", ""))
    password = str(data.get("password", ""))
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    if is_rate_limited(ip):
        return jsonify({"error": "Too many failed attempts. Try again in 5 minutes."}), 429

    hashed = hashlib.sha256(password.encode()).hexdigest()
    if username in USERS and USERS[username] == hashed:
        LOGIN_ATTEMPTS[ip].clear()
        session["user"] = username
        session["login_time"] = time.time()
        return jsonify({"message": "Login successful", "user": username}), 200

    LOGIN_ATTEMPTS[ip].append(time.time())
    attempts_left = MAX_ATTEMPTS - len(LOGIN_ATTEMPTS[ip])
    return jsonify({"error": "Invalid credentials", "attempts_remaining": max(0, attempts_left)}), 401


@app.route("/logout", methods=["POST"])
@require_auth
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@app.route("/profile", methods=["GET"])
@require_auth
def profile():
    user = session["user"]
    return jsonify({
        "user": user,
        "role": "admin" if user == "admin" else "user",
        "login_time": session.get("login_time")
    }), 200


@app.route("/admin/users", methods=["GET"])
@require_auth
def admin_users():
    if session.get("user") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    return jsonify({"users": list(USERS.keys())}), 200


if __name__ == "__main__":
    app.run(debug=False, port=5001)
