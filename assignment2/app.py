import json
from flask import Flask, request
import db

DB = db.DatabaseDriver()

app = Flask(__name__)


@app.route("/")
def hello_world():
    """
    Says hello to the world with default path
    """
    return "Hello world!"


@app.route("/api/users/")
def get_all_users():
    """
    Endpoint for getting all users from the database
    """
    return json.dumps({"users": DB.get_all_users()}), 200


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user in the database
    """
    body = json.loads(request.data)
    try:
        name = body.get("name")
        username = body.get("username")
        balance = body.get("balance", 0)
    except:
        return json.dumps({"error": "Username or name field not inputted"}), 400

    user_id = DB.create_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Something went wrong creating a task"}), 400

    return json.dumps(user), 201


@app.route("/api/user/<int:uid>/")
def get_specific_user(uid):
    """
    Endpoint to get a user by its id
    """
    user = DB.get_user_by_id(uid)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    return json.dumps(user), 200


@app.route("/api/user/<int:uid>/", methods=["DELETE"])
def delete_specific_user(uid):
    """
    Endpoint to delete a user by its id
    """
    user = DB.get_user_by_id(uid)
    if user is None:
        return json.dumps({"error": "User not found"}), 404

    DB.delete_user_by_id(uid)

    return json.dumps(user), 200


@app.route("/api/send/", methods=["POST"])
def send():
    """
        Endpoint for sending money from one user to another
    """
    body = json.loads(request.data)
    try:
        amount = body.get("amount")
        receiver_id = body.get("receiver_id")
        sender_id = body.get("sender_id")
    except:
        return json.dumps({"error": "Required field unspecified"}), 400

    user_sender = DB.get_user_by_id(sender_id)
    user_receiver = DB.get_user_by_id(receiver_id)
    if (user_sender is None or user_receiver is None):
        return json.dumps({"error": "User not found"}), 404

    if (DB.get_balance(sender_id) < amount):
        return json.dumps({"error": "Sender balance low"}), 400
    if (amount < 0):
        return json.dumps({"error": "Amount cannot be negative"}), 400
    DB.send_money(sender_id, receiver_id, amount)
    return body, 200

@app.route("/api/extra/users/", methods = ["POST"])

def create_password():
    """
    Endpoint for needing a password when creating user
    """
    body = json.loads(request.data)
    try: 
        input_password = body.get("password")
    except: 
        return json.dumps({"Unauthorized error": "No password sent"}), 401
    try:
        name = body.get("name")
        username = body.get("username")
        balance = body.get("balance", 0)
    except:
        return json.dumps({"error": "Username or name field not inputted"}), 400

    user_id = DB.create_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Something went wrong creating a task"}), 400
    DB.set_password(user_id, input_password)
    return json.dumps(user), 201


@app.route("/api/extra/user/<int:id>/", methods = ["POST"])
def v_password(id): 
    """
    Endpoint to verify password before returning a specific user by id
    """
    body = json.loads(request.data)
    try: 
        input_password = body.get("password")
    except: 
        return json.dumps({"Unauthorized error": "No password sent"}), 401

    user = DB.get_user_by_id(id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    
    if (DB.verify_password(id, input_password)): 
        return json.dumps(user), 200
    return json.dumps({"Unauthorized error": "Wrong password"}), 401

@app.route("/api/extra/send/", methods = ["POST"])
def verify_send_password(): 
    """
    Endpoint for verifying the password of the user before sending money
    """
    body = json.loads(request.data)
    try: 
        input_password = body.get("password")
        sender_id = body.get("sender_id")
    except: 
        return json.dumps({"Unauthorized error": "No password sent"}), 401

    if (DB.verify_password(sender_id, input_password)): 
        send()
    return json.dumps({"Unauthorized error": "Wrong password"}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
