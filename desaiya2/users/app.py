import hashlib
import sqlite3
import os
import json
import requests
from flask import Flask, request,jsonify
from auth import generate_jwt,verify_token

app = Flask(__name__)
db_name = "user.db"
sql_file = "users.sql"
db_flag = False 


@app.route('/', methods=(['GET']))
def index():
	MICRO2URL = "http://localhost:5001/test_micro"
	r = requests.get(url = MICRO2URL)
	data = r.json()

	return data


@app.route('/test_micro', methods=(['GET']))
def test_micro():

	return "This is Microservice 1"

def create_db():
    conn = sqlite3.connect(db_name)
    
    with open(sql_file, 'r') as sql_startup:
        init_db = sql_startup.read()
        
    cursor = conn.cursor()
    cursor.executescript(init_db)
    conn.commit()
    conn.close()
    
    global db_flag
    db_flag = True
    return conn

def get_db():
	if not db_flag:
		create_db()
	conn = sqlite3.connect(db_name)
	return conn


@app.route('/clear', methods=['GET'])
def clear():
    """Clear the database by deleting the DB file""" 
    try:
        if os.path.exists(db_name):
            os.remove(db_name)
            create_db()
        return "Database cleared"
    except Exception as e:
        return f"Error clearing database: {str(e)}"


def already_exists(username, email):
  """Check if username or email already exists."""
  db = get_db()
  cursor = db.cursor()
 
  cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?;", (username,))
  exist_name = cursor.fetchone()[0] >= 1
  cursor.execute("SELECT COUNT(*) FROM users WHERE email_address = ?;", (email,))
  exist_email = cursor.fetchone()[0] >= 1

  db.close()
  return exist_name, exist_email


def password_requirements(password, username, first_name, last_name, error):
    """Check password requirements"""

    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if password.islower() or password.isupper() or password.isdigit() or password.isalpha():
        return False, "Password must contain a mix of upper, lower, and numeric characters"
    if username in password or first_name in password or last_name in password:
        return False, "Password cannot contain personal information"
    return True, None


@app.route('/create_user', methods=['POST'])
def create_user():
    """Create a new user and store hashed password."""

    first = request.form.get('first_name')
    last = request.form.get('last_name')
    username = request.form.get('username')
    email = request.form.get('email_address')
    password = request.form.get('password')
    salt = request.form.get('salt')
    employee = request.form.get('employee')
    

    # Validating required fields
    status, pass_hash, error = 1, 'NULL', None
    required_fields = [first, last, username, email, password, salt, employee]
    error_messages = ["First name is required", "Last name is required", "Username is required", "Email address is required", "Password is required", "Salt is required","Employee status is required"]

    for i, field in enumerate(required_fields):
        if not field:
            error = error_messages[i]
            break

    # Checking for duplicate username or email        
    if not error:
        exist_name, exist_email = already_exists(username, email)
        if exist_name:
            status = 2
        elif exist_email:
            status= 3

    # Checking password validity
    if not error:
        valid, error = password_requirements(password, username, first, last, error)
        if not valid:
            status = 4

    # Convert employee to integer 
    if not error:
        employee = 1 if str(employee).lower() == 'true' or employee == '1' else 0

    if error is None:
        pass_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        conn = get_db()
        curr = conn.cursor()
        curr.execute(
            "INSERT INTO users (first_name, last_name, username, email_address, current_password, salt, employee) VALUES (?, ?, ?, ?, ?, ?, ?);",
            (first, last, username, email, pass_hash, salt, employee),
        )
        conn.commit()
        if status == 1:
        # log the user‐creation event
            requests.post("http://logs:5000/log",json={"event": "user_creation","user":  username,"name":  "NULL"})
        conn.close()
    return jsonify({"status": status, "pass_hash": pass_hash}), 200



@app.route('/login', methods=['POST'])
def login():
    """Authenticate user and return a JWT if successful."""

    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({"status": 2, "jwt": "NULL"})

    conn = get_db()
    curr = conn.cursor()

    user_data = curr.execute('SELECT salt, current_password,employee FROM users WHERE username = ?;', (username,)).fetchone()
    status, token = (2, 'NULL') if not user_data else (1, None)

    if status == 1:
        salt, stored_password,employee = user_data
        hashed_input_password = hashlib.sha256((password + salt).encode()).hexdigest()

         # Verify password match
        if hashed_input_password != stored_password:
            status, token = 2, 'NULL'
        else:
            token = generate_jwt(username)
            requests.post("http://logs:5000/log",json={"event": "login","user":  username,"name":  "NULL"})

    conn.close()
    return jsonify({"status": status, "jwt": token or "NULL"})


# This function checks if an user is an employee
@app.route('/verify', methods=['POST'])
def verify():
    token = request.headers.get('Data')
    if not token:
        return jsonify({"employee": False,"username":None})

    username = verify_token(token)
    print('token',token)
    if not username:
        return jsonify({"employee": False,"username":None})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT employee FROM users WHERE username = ?", (username,))
    result = cur.fetchone()
    conn.close()

    if not result:
        return jsonify({"employee": False,"username":None})
    if result[0] == 0:
        return jsonify({"employee": False,"username":username})
    return jsonify({"employee": True,"username":username})
