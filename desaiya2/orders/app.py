from flask import Flask,jsonify,request
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return "Service is up!"


@app.route('/clear', methods=['GET'])
def clear():
    """Clear the database by deleting the DB file""" 
    return "Database cleared"



@app.route('/order', methods=['POST'])
def order():

    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": 2, "cost": "NULL"})

    response = requests.post("http://user:5000/verify",headers={"Data": token})

    try:
        users = response.json()
    except ValueError:
        return jsonify({"status": 2, "cost": "NULL"})
    
    username = users.get("username")
    if not username:
        return jsonify({"status": 2, "cost": "NULL"})

    # Parse the 'order' form field
    orders = request.form.get('order')
    if not orders:
        return jsonify({"status": 2, "cost": "NULL"})
    order_list = json.loads(orders)

    #For each item, look up price and accumulate
    total_cost = 0.0
    for item in order_list:
        product_name = item.get("product")
        quantity     = item.get("quantity", 0)

        if not product_name:
            continue
        if not quantity:
            continue
        if quantity<=0:
            continue

        product_url = requests.get("http://products:5000/products",params={"product_name": product_name})

        # If service error or no such product
        if product_url.status_code != 200:
           return jsonify({"status": 3, "cost": "NULL"})
        prod_list = product_url.json()
        if not prod_list:
           return jsonify({"status": 3, "cost": "NULL"})


        price = prod_list[0].get("price", 0)
        total_cost += price * quantity
        requests.post("http://logs:5000/log",json={"event": "order","user":  username,"name":  "NULL"})

    cost = f"{total_cost:.2f}"
    return jsonify({"status": 1, "cost": cost})