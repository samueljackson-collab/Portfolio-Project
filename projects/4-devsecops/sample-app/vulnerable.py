#!/usr/bin/env python3
"""
INTENTIONALLY VULNERABLE APPLICATION - FOR SECURITY DEMONSTRATION ONLY

This file contains common security vulnerabilities for demonstrating
security scanning tools. DO NOT use this code in production.

Each vulnerability is labeled with its type and CWE reference.
"""

import hashlib
import os
import pickle
import subprocess
import sqlite3
import tempfile
from flask import Flask, request, render_template_string, redirect

app = Flask(__name__)

# VULNERABILITY: Hardcoded credentials (CWE-798)
# Tools that detect: Gitleaks, TruffleHog, detect-secrets
DATABASE_PASSWORD = "super_secret_password_123"
API_KEY = "sk-1234567890abcdef1234567890abcdef"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"


# VULNERABILITY: SQL Injection (CWE-89)
# Tools that detect: Semgrep, Bandit, CodeQL
@app.route('/user')
def get_user():
    user_id = request.args.get('id')
    # BAD: Direct string interpolation in SQL query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    conn = sqlite3.connect('app.db')
    cursor = conn.execute(query)  # noqa: S608
    return str(cursor.fetchall())


# VULNERABILITY: Command Injection (CWE-78)
# Tools that detect: Semgrep, Bandit, CodeQL
@app.route('/ping')
def ping_host():
    host = request.args.get('host')
    # BAD: User input directly in shell command
    result = subprocess.run(
        f"ping -c 1 {host}",
        shell=True,  # noqa: S602
        capture_output=True
    )
    return result.stdout


# VULNERABILITY: Path Traversal (CWE-22)
# Tools that detect: Semgrep, Bandit
@app.route('/file')
def read_file():
    filename = request.args.get('name')
    # BAD: No validation of file path
    filepath = f"/var/data/{filename}"
    with open(filepath, 'r') as f:
        return f.read()


# VULNERABILITY: Cross-Site Scripting (XSS) (CWE-79)
# Tools that detect: Semgrep, Bandit
@app.route('/greet')
def greet():
    name = request.args.get('name')
    # BAD: User input rendered without escaping
    return render_template_string(f"<h1>Hello, {name}!</h1>")


# VULNERABILITY: Insecure Deserialization (CWE-502)
# Tools that detect: Semgrep, Bandit
@app.route('/load', methods=['POST'])
def load_data():
    data = request.get_data()
    # BAD: Deserializing untrusted data
    obj = pickle.loads(data)  # noqa: S301
    return str(obj)


# VULNERABILITY: Weak Cryptography (CWE-327)
# Tools that detect: Semgrep, Bandit
def hash_password(password):
    # BAD: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()  # noqa: S324


# VULNERABILITY: Insecure Random (CWE-330)
# Tools that detect: Semgrep, Bandit
import random  # noqa: E402
def generate_token():
    # BAD: Using predictable random for security tokens
    return ''.join(random.choices('abcdef0123456789', k=32))


# VULNERABILITY: Open Redirect (CWE-601)
# Tools that detect: Semgrep
@app.route('/redirect')
def unsafe_redirect():
    url = request.args.get('url')
    # BAD: Redirecting to user-controlled URL
    return redirect(url)


# VULNERABILITY: XML External Entity (XXE) (CWE-611)
# Tools that detect: Semgrep, Bandit
from xml.etree.ElementTree import parse as xml_parse  # noqa: E402
def parse_xml(xml_file):
    # BAD: XML parsing without disabling external entities
    tree = xml_parse(xml_file)
    return tree.getroot()


# VULNERABILITY: Server-Side Request Forgery (SSRF) (CWE-918)
# Tools that detect: Semgrep
import requests  # noqa: E402
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    # BAD: Fetching user-controlled URL
    response = requests.get(url)
    return response.text


# VULNERABILITY: Hardcoded IP Address (CWE-1188)
# Tools that detect: Semgrep
ADMIN_SERVER = "192.168.1.100"
DATABASE_HOST = "10.0.0.50"


# VULNERABILITY: Debug Mode in Production (CWE-489)
# Tools that detect: Bandit
DEBUG = True
TESTING = True


# VULNERABILITY: Missing HTTPS Enforcement
# Tools that detect: Semgrep
@app.route('/login', methods=['POST'])
def login():
    # BAD: No HTTPS enforcement, credentials sent in plain text
    username = request.form.get('username')
    password = request.form.get('password')
    # Check credentials (vulnerable to timing attack)
    if username == "admin" and password == DATABASE_PASSWORD:
        return "Login successful"
    return "Login failed"


# VULNERABILITY: Insufficient Logging (CWE-778)
# No logging of security events
def process_payment(card_number, amount):
    # BAD: No logging of financial transaction
    return True


# VULNERABILITY: Race Condition (CWE-362)
balance = 1000
def withdraw(amount):
    global balance
    # BAD: Non-atomic check-then-act
    if balance >= amount:
        # Time-of-check to time-of-use vulnerability
        balance -= amount
        return True
    return False


if __name__ == '__main__':
    # VULNERABILITY: Running with debug mode (CWE-489)
    app.run(debug=True, host='0.0.0.0')  # noqa: S201
