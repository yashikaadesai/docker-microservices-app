from flask import Flask,request,jsonify
import requests


app = Flask(__name__)

@app.route('/')
def index():
    return "Service is up!"


@app.route('/clear', methods=['GET'])
def clear():
    """Clear the database by deleting the DB file""" 
    return "Database cleared"


# This function searches for a product or the name 
@app.route('/search',methods=['GET'])
def search():
       
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": 2, "data": "NULL"})

    status = requests.post("http://user:5000/verify", headers={"Data": token})

    try:
        users = status.json()
    except ValueError:
        return jsonify({"status": 2, "data": "NULL"})
    
    username = users.get("username")
    if not username:
        return jsonify({"status": 2, "data": "NULL"})

    name = request.args.get('product_name')
    category = request.args.get('category')
    has_name = bool(name)
    has_category = bool(category)

    if (has_name and has_category) or (not has_name and not has_category):
        return jsonify({'status': 2, 'data': 'NULL'})

    product_url = "http://products:5000/products"

    if has_name:
        params = {'product_name': name}
    else:
        params = {'category': category}

    response = requests.get(product_url, params=params)
    products = response.json()

    if not products:
        return jsonify({"status": 3, "data": []})

    out = [{"product_name": p["product_name"], "price":p["price"], "category":p["category"],"last_mod":username}for p in products]
    
    requests.post("http://logs:5000/log",json={"event": "search","user":  username,"name":  name if name else category})
    return jsonify({"status": 1, "data": out})
