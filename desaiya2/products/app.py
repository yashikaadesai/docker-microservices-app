import sqlite3
import os
import json
import hashlib
import hmac
import base64
import requests
from flask import Flask, request,jsonify

app = Flask(__name__)

db_name = "products.db"
sql_file = "products.sql"
db_flag = False

@app.route('/', methods=(['GET']))
def index():

	return json.dumps({'1': 'test', '2': 'test2'})

@app.route('/test_micro', methods=(['GET']))
def test_micro():

	return json.dumps({"response": "This is a message from Microservice 2"})

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


@app.route('/create_product', methods=['POST'])
def create_product():
    print("CREATE PRODUCT ENDPOINT CALLED")

    token = request.headers.get('Authorization')
    # print("token : " , token)
    if not token:
        return jsonify({"status": 2,"username":username})
    
    
    # Check if the user is an employee 
    employee_status = requests.post("http://user:5000/verify", headers={"Data": token}).json()
    username= employee_status.get("username")
    # fullReturn = employee_status.json()

    if username is None:
        return jsonify({"status":2})
    
    if not employee_status.get("employee",False):
        return jsonify({"status": 2})

    name = request.form.get('name')
    price = request.form.get('price')
    category = request.form.get('category')

    if not name or not price or not category:
        return jsonify({"status": 2})
    conn=get_db()
    curr=conn.cursor()
    try:
        curr.execute("INSERT INTO products (name, price, category) VALUES (?, ?, ?)", (name, price, category))
        conn.commit()
        requests.post("http://logs:5000/log",json={"event": "product_creation","user":  username,"name":  name} )

    except:
        conn.close()
        return jsonify({"status":2})
    return jsonify({"status":1})
       

#allows you to edit the product
@app.route('/edit_product', methods=['POST'])
def edit_product():
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": 2})

    employee_status = requests.post("http://user:5000/verify", headers={"Data": token})

    try:
        status = employee_status.json()
    except ValueError:
        return jsonify({"status": 2})

    username = status.get("username")
    employee=status.get("employee")

    if not username:
        return jsonify({"status": 2})
    
    if not employee:
        return jsonify({"status": 3})


    name = request.form.get('name')
    new_price = request.form.get('new_price')
    new_category = request.form.get('new_category')

    if not name or bool(new_price) == bool(new_category):
        return jsonify({"status": 2})

    conn = get_db()
    cur = conn.cursor()
    try:
        if new_price:
            cur.execute("UPDATE products SET price = ? WHERE name = ?",(new_price, name))
        else:
            cur.execute("UPDATE products SET category = ? WHERE name = ?",(new_category, name))

        conn.commit()
        requests.post("http://logs:5000/log",json={"event": "product_edit","user":  username,"name":  name})
        conn.close()
        return jsonify({"status": 1})
    except Exception:
        conn.close()
        return jsonify({"status": 2})
    


@app.route('/products', methods=['GET'])
def get_products():

    name = request.args.get('name') 
    if not name:
        name = request.args.get('product_name')
    category = request.args.get('category')

    if (name and category) or (not name and not category):
        return jsonify({"status":2,"data": None})

    conn = get_db()
    cur = conn.cursor()
    if name:
        rows = cur.execute("SELECT name, price, category FROM products WHERE name = ?",(name,)).fetchall()
    else:
        rows = cur.execute("SELECT name, price, category FROM products WHERE category = ?",(category,)).fetchall()
    conn.close()

    products=[]
    for r in rows:
        product={}
        product["product_name"]=r[0]
        product["price"] = r[1]
        product["category"] = r[2]
        products.append(product)
    return jsonify(products), 200

