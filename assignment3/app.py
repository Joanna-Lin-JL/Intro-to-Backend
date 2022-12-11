from datetime import datetime
import json

import db
from flask import Flask
from flask import request

DB = db.DatabaseDriver()


app = Flask(__name__)


def check_balance(sender, amount):
    if (DB.get_balance(sender) < amount):
        return False
    return True


def success_response(body, code=200):
    """
    Give success response of 200 given the body
    """
    return json.dumps(body), code


def failure_response(message, code=404):
    """
    Give failure response of 404 given error message
    """
    return json.dumps({"error": message}), code


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
    return success_response({"users": DB.get_all_users()})


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a user in the database
    """
    body = json.loads(request.data)
    name = body.get("name", None)
    username = body.get("username", None)
    balance = body.get("balance", 0)
    if name is None or username is None:
        return failure_response("Username or name field not inputted", 400)
    user_id = DB.create_user(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return failure_response("Something went wrong creating a user", 400)

    return success_response(user, 201)


@app.route("/api/users/<int:uid>/")
def get_specific_user(uid):
    """
    Endpoint to get a user by its id
    """
    user = DB.get_user_by_id(uid)
    if user is None:
        return failure_response("User not found")

    return success_response(user)


@app.route("/api/users/<int:uid>/", methods=["DELETE"])
def delete_specific_user(uid):
    """
    Endpoint to delete a user by its id
    """
    user = DB.get_user_by_id(uid)
    if user is None:
        return failure_response("User not found")

    DB.delete_user_by_id(uid)
    return success_response(user)


@app.route("/api/transactions/", methods=["POST"])
def make_transactions():
    """
    Endpoint for making a transaction
    """
    body = json.loads(request.data)
    sender = body.get("sender_id", None)
    receiver = body.get("receiver_id", None)
    amount = body.get("amount", None)
    message = body.get("message")
    if (sender is None or receiver is None or amount is None):
        return failure_response("Required fields not filled", 400)

    accepted = body.get("accepted", None)

    if (accepted is not None and accepted):
        if check_balance(sender, amount):
            DB.send_money(sender, receiver, amount)
        else:
            return failure_response("Sender balance low", 403)

    timestamp = datetime.now().__str__()
    txn_id = DB.create_transactions(
        sender, receiver, timestamp, amount, message, accepted)
    txn = DB.get_transaction(txn_id)
    if txn is None:
        return failure_response("Something went wrong making transaction", 400)
    return success_response(txn, 201)


@app.route("/api/transactions/<int:tid>/", methods=["POST"])
def action(tid):
    txn = DB.get_transaction(tid)
    if txn is None:
        return failure_response("Transaction not found")

    accepted = txn.get("accepted")
    if (accepted is not None):
        if accepted:
            return failure_response("transaction already accepted", 403)
        else:
            return failure_response("transaction already denied", 403)

    body = json.loads(request.data)
    accepted = body.get("accepted")
    if (accepted):
        if (check_balance(txn.get("sender_id"), txn.get("amount"))):
            DB.send_money(txn.get("sender_id"), txn.get(
                "receiver_id"), txn.get("amount"))
        else:
            return failure_response("Sender balance low", 403)

    DB.update_transaction(tid, datetime.now().__str__(), accepted)
    txn = DB.get_transaction(tid)
    return success_response(txn)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
