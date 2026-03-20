from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "selenium-test-secret-key-2025"

USERS = {"admin": "Admin@1234", "demo": "Demo@5678", "test": "Test@9999"}

LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Demo App - Login</title></head>
<body>
  <h1>Sign In</h1>
  {% if error %}<p id="error-msg" style="color:red">{{ error }}</p>{% endif %}
  <form method="post" action="/login">
    <label>Username: <input type="text" name="username" id="username"></label><br>
    <label>Password: <input type="password" name="password" id="password"></label><br>
    <button type="submit" id="login-btn">Login</button>
  </form>
</body>
</html>"""

DASHBOARD_PAGE = """
<!DOCTYPE html>
<html>
<head><title>Dashboard</title></head>
<body>
  <h1 id="welcome-msg">Welcome, {{ user }}!</h1>
  <nav>
    <a href="/profile" id="nav-profile">Profile</a> |
    <a href="/settings" id="nav-settings">Settings</a> |
    <a href="/logout" id="nav-logout">Logout</a>
  </nav>
  <div id="dashboard-content">
    <h2>Dashboard</h2>
    <p>You are logged in as <span id="current-user">{{ user }}</span></p>
  </div>
</body>
</html>"""

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login_page"))

@app.route("/login", methods=["GET"])
def login_page():
    return render_template_string(LOGIN_PAGE, error=None)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    if username in USERS and USERS[username] == password:
        session["user"] = username
        return redirect(url_for("dashboard"))
    return render_template_string(LOGIN_PAGE, error="Invalid username or password")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return render_template_string(DASHBOARD_PAGE, user=session["user"])

@app.route("/profile")
def profile():
    if "user" not in session:
        return redirect(url_for("login_page"))
    return f"<h1>Profile: {session['user']}</h1><a href='/logout'>Logout</a>"

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=False, port=5002)
