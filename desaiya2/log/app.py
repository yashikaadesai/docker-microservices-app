from flask import Flask,request,jsonify
import requests
import os 
import sqlite3

app = Flask(__name__)

db_name = "logs.db"
sql_file = "logs.sql"
db_flag = False

@app.route('/')
def index():
    return "Service is up!"

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



def log_event(event, user, name):
    requests.post("http://logs:5000/log", json={"event": event,"user":  user,"name":  name })



@app.route('/log', methods=['POST'])
def log():
    data = request.get_json()
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("INSERT INTO logs (event, user, name) VALUES (?, ?, ?)",(data["event"], data["user"], data["name"]))
    conn.commit()
    conn.close()
    return jsonify({"status":1}), 200


@app.route('/view_log', methods=['GET'])
def view_log():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": 2, "data": "NULL"})

    response = requests.post("http://user:5000/verify", headers={"Data": token})
    info = response.json()

    username = info.get("username")
    is_employee = info.get("employee", False)

    if not username:
        return jsonify({"status": 2, "data": "NULL"})

    user    = request.args.get('username')
    product = request.args.get('product')

    if not user and not product:
        return jsonify({"status": 2, "data": "NULL"})

    if user and product:
        return jsonify({"status": 2, "data": "NULL"})

    if user:
        column = 'user'
        value  = user
        if username != user and not is_employee:
            return jsonify({"status": 3, "data": "NULL"})
    else:
        column = 'name'
        value  = product

        if not is_employee:
            return jsonify({"status": 3, "data": "NULL"})

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    result = f"SELECT event, user, name FROM logs WHERE {column} = ? ORDER BY id"
    rows = cur.execute(result, (value,)).fetchall()
    conn.close()

    data = {}
    count = 1
    for event, user, name in rows:
        data[count] = {"event": event,"user":  user,"name":  name}
        count += 1
    return jsonify({"status": 1, "data": data})