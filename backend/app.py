from flask import Flask, request, session, jsonify, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from pymongo import MongoClient
import bcrypt
from flask_cors import CORS
from datetime import datetime
import random
from bson.objectid import ObjectId
import logging

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.secret_key = "testing"

def MongoDB():
    #client = MongoClient('localhost',27017)
    client = MongoClient('mongodb+srv://michalplaza9:Yfsa6BO4XynWgF3l@bdlab.h7rrtcr.mongodb.net/?retryWrites=true&w=majority&appName=bdlab')
    db = client.get_database('total_records')
    return db

db = MongoDB()
records = db.register
offers = db.offers
wallets = db.wallets
transactions = db.transactions

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, user_id, email):
        self.id = str(user_id)
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    user = records.find_one({"_id": ObjectId(user_id)})
    if user:
        return User(user['_id'], user['email'])
    return None

@app.route("/add_offer", methods=['POST'])
def add_offer():
    data = request.get_json()
    from_user_email = data.get('fromUser')
    from_value = float(data.get('fromValue'))
    from_currency = data.get('fromCurrency')
    to_value = float(data.get('toValue'))
    to_currency = data.get('toCurrency')

    if not from_user_email or not from_value or not from_currency or not to_value or not to_currency:
        return jsonify({"message": "Missing data"}), 400

    from_user = records.find_one({"email": from_user_email})
    if not from_user:
        return jsonify({"message": "User not found"}), 404

    from_user_wallet = wallets.find_one({"user": str(from_user['_id'])})
    if not from_user_wallet:
        return jsonify({"message": "Wallet not found"}), 404

    # Check if user has enough balance
    for currency in from_user_wallet['currencies']:
        if currency['currency'] == from_currency:
            if currency['value'] < from_value:
                return jsonify({"message": f"Not enough {from_currency} in wallet"}), 400
            else:
                currency['value'] -= from_value  # Deduct the offered value

    # Find all matching offers
    matching_offers = list(offers.find({
        "from_currency": to_currency,
        "to_currency": from_currency,
        "to_value": {"$lte": from_value}
    }).sort([("to_value", -1)]))  # Sort by to_value descending

    total_to_value = 0
    offers_to_use = []

    # Find the combination of offers that matches or is more beneficial
    for offer in matching_offers:
        total_to_value += offer['to_value']
        offers_to_use.append(offer)
        if total_to_value >= to_value:
            break

    if total_to_value >= to_value:
        for offer in offers_to_use:
            to_user_email = offer['from_user']
            to_user = records.find_one({"email": to_user_email})

            if not to_user:
                return jsonify({"message": "Matching user not found"}), 404

            to_user_wallet = wallets.find_one({"user": str(to_user['_id'])})
            if not to_user_wallet:
                return jsonify({"message": "Matching user wallet not found"}), 404

            # Add value to the matching user's wallet
            for currency in to_user_wallet['currencies']:
                if currency['currency'] == to_currency:
                    currency['value'] += offer['to_value']
                if currency['currency'] == from_currency:
                    currency['value'] -= offer['from_value']

            # Update wallets in database
            wallets.update_one({"user": str(from_user['_id'])}, {"$set": from_user_wallet})
            wallets.update_one({"user": str(to_user['_id'])}, {"$set": to_user_wallet})

            # Insert transaction into transactions collection
            transaction = {
                'from_user': from_user_email,
                'from_value': offer['from_value'],
                'from_currency': from_currency,
                'to_user': to_user_email,
                'to_value': offer['to_value'],
                'to_currency': to_currency,
                'date': datetime.utcnow()
            }
            transactions.insert_one(transaction)

            # Remove the matched offer from the database
            offers.delete_one({"_id": offer['_id']})

        return jsonify({"message": "Transaction completed successfully"}), 201

    # If no matching offer, create new offer
    offer = {
        'from_user': str(from_user_email),
        'from_value': from_value,
        'from_currency': str(from_currency),
        'to_value': to_value,
        'to_currency': str(to_currency),
        'date': datetime.utcnow()
    }

    try:
        offers.insert_one(offer)
        return jsonify({"message": "Offer added successfully"}), 201
    except Exception as e:
        print("Error while inserting offer:", e)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/get_offers", methods=['GET'])
def get_offers():
    try:
        all_offers = list(offers.find({}, {'_id': 1, 'from_user': 1, 'from_value': 1, 'from_currency': 1, 'to_value': 1, 'to_currency': 1, 'date': 1}))
        print("Fetched Offers:", all_offers)  # Debugging line
        for offer in all_offers:
            offer['_id'] = str(offer['_id'])  # Convert ObjectId to string
        return jsonify(all_offers), 200
    except Exception as e:
        print("Error while fetching offers:", e)
        return jsonify({"message": "Internal server error"}), 500



@app.route("/make_transaction/<offer_id>", methods=['POST'])
@login_required
def make_transaction(offer_id):
    try:
        offer = offers.find_one({"_id": ObjectId(offer_id)})
        if not offer:
            logging.error(f"Offer {offer_id} not found")
            return jsonify({"message": "Offer not found"}), 404
        from_user_email = offer['from_user']
        to_user_email = request.json.get('userEmail')

        logging.info(f"Processing transaction from {from_user_email} to {to_user_email}")
        from_user = records.find_one({"email": from_user_email})
        to_user = records.find_one({"email": to_user_email})

        if not from_user:
            logging.error(f"From user {from_user_email} not found")
            return jsonify({"message": "From user not found"}), 404
        if not to_user:
            logging.error(f"To user {to_user_email} not found")
            return jsonify({"message": "To user not found"}), 404
        from_user_wallet = wallets.find_one({"user": str(from_user['_id'])})
        to_user_wallet = wallets.find_one({"user": str(to_user['_id'])})

        if not from_user_wallet:
            logging.error(f"From user wallet for {from_user_email} not found")
            return jsonify({"message": "From user wallet not found"}), 404
        if not to_user_wallet:
            logging.error(f"To user wallet for {to_user_email} not found")
            return jsonify({"message": "To user wallet not found"}), 404
        from_currency = offer['from_currency']
        to_currency = offer['to_currency']
        from_value = float(offer['from_value'])
        to_value = float(offer['to_value'])

        def update_wallet(wallet: dict, currency: str, value: float, operation: str) -> bool:
            for c in wallet['currencies']:
                if c['currency'] == currency:
                    if operation == 'subtract':
                        if c['value'] < value:
                            logging.error(f"Insufficient funds: currency={currency}, value={value}, wallet={wallet}")
                            return False
                        c['value'] -= value
                    elif operation == 'add':
                        c['value'] += value
                    return True
            logging.error(f"Currency {currency} not found in wallet: {wallet}")
            return False

        # Update from_user wallet
        if not update_wallet(from_user_wallet, from_currency, from_value, 'subtract'):
            return jsonify({"message": f"Not enough {from_currency} in from user's wallet"}), 400
        if not update_wallet(to_user_wallet, from_currency, from_value, 'add'):
            return jsonify({"message": "Error updating to user's wallet"}), 500

        # Update to_user wallet
        if not update_wallet(to_user_wallet, to_currency, to_value, 'subtract'):
            return jsonify({"message": f"Not enough {to_currency} in to user's wallet"}), 400
        if not update_wallet(from_user_wallet, to_currency, to_value, 'add'):
            return jsonify({"message": "Error updating from user's wallet"}), 500
        wallets.update_one({"user": str(from_user['_id'])}, {"$set": from_user_wallet})
        wallets.update_one({"user": str(to_user['_id'])}, {"$set": to_user_wallet})

        # Insert transaction into transactions collection
        transaction = {
            'from_user': from_user_email,
            'from_value': from_value,
            'from_currency': from_currency,
            'to_user': to_user_email,
            'to_value': to_value,
            'to_currency': to_currency,
            'date': datetime.utcnow()
        }
        transactions.insert_one(transaction)

        offers.delete_one({"_id": ObjectId(offer_id)})
        logging.info(f"Transaction completed successfully from {from_user_email} to {to_user_email}")
        return jsonify({"message": "Transaction completed successfully"}), 200

    except Exception as e:
        logging.error(f"Error while making transaction: {e}", exc_info=True)
        return jsonify({"message": "Internal server error"}), 500


@app.route("/register", methods=['POST'])
def register():
    if "email" in session:
        return jsonify({"message": "Already logged in"}), 400

    data = request.get_json()
    user = data.get("fullname")
    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")

    user_found = records.find_one({"name": user})
    email_found = records.find_one({"email": email})
    if user_found:
        return jsonify({"message": 'There already is a user by that name'}), 400
    if email_found:
        return jsonify({"message": 'This email already exists in database'}), 400
    if password1 != password2:
        return jsonify({"message": 'Passwords should match!'}), 400
    else:
        hashed = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())
        user_input = {'name': user, 'email': email, 'password': hashed}
        records.insert_one(user_input)
        user_data = records.find_one({"email": email})

        wallet_data = {
            "user": str(user_data['_id']),
            "currencies": [
                {"currency": "USD", "value": random.randint(1000, 5000)},
                {"currency": "EUR", "value": random.randint(1000, 5000)},
                {"currency": "PLN", "value": random.randint(1000, 5000)},
                {"currency": "GBP", "value": random.randint(1000, 5000)},
                {"currency": "JPY", "value": random.randint(1000, 5000)},
                {"currency": "CZK", "value": random.randint(1000, 5000)}
            ]
        }
        wallets.insert_one(wallet_data)

        return jsonify({"message": "Registered successfully", "redirect": True}), 201

@app.route("/login", methods=["POST"])
def login():
    if "email" in session:
        return jsonify({"message": "Already logged in"}), 400

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    email_found = records.find_one({"email": email})
    if email_found:
        email_val = email_found['email']
        passwordcheck = email_found['password']
        if bcrypt.checkpw(password.encode('utf-8'), passwordcheck):
            user_obj = User(email_found["_id"], email_val)
            login_user(user_obj)
            session["email"] = email_val
            session["user_id"] = str(email_found["_id"])
            return jsonify({"message": "Login successful", "redirect": True}), 200
        else:
            return jsonify({"message": "Wrong password"}), 400
    else:
        return jsonify({"message": "Email not found"}), 404

@app.route('/logged_in')
@login_required
def logged_in():
    return jsonify({"email": current_user.email}), 200

@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    session.pop("email", None)
    session.pop("user_id", None)
    logout_user()
    return jsonify({"message": "Logged out"}), 200

@app.route("/wallet", methods=['GET'])
@login_required
def wallet():
    user_id = session["user_id"]
    user_wallet = wallets.find_one({"user": user_id}, {"_id": 0, "currencies": 1})
    if not user_wallet:
        return jsonify({"error": "Wallet not found"}), 404

    user_transactions = list(transactions.find({"user": user_id}, {"_id": 0}))

    wallet_data = {
        "wallet": user_wallet["currencies"],
        "transactions": user_transactions
    }

    return jsonify(wallet_data), 200

@app.route("/cancel_offer/<offer_id>", methods=['DELETE'])
def cancel_offer(offer_id):
    try:
        print(f"Received offer_id: {offer_id}")  # Logowanie ID oferty
        offer = offers.find_one({"_id": ObjectId(offer_id)})
        if not offer:
            return jsonify({"message": "Offer not found"}), 404

        from_user = records.find_one({"email": offer['from_user']})
        if not from_user:
            return jsonify({"message": "User not found"}), 404

        from_user_wallet = wallets.find_one({"user": str(from_user['_id'])})
        if not from_user_wallet:
            return jsonify({"message": "Wallet not found"}), 404

        # Return the offered value to the user's wallet
        for currency in from_user_wallet['currencies']:
            if currency['currency'] == offer['from_currency']:
                currency['value'] += offer['from_value']

        # Update wallet in database
        wallets.update_one({"user": str(from_user['_id'])}, {"$set": from_user_wallet})

        # Remove the offer from the database
        offers.delete_one({"_id": ObjectId(offer_id)})

        return jsonify({"message": "Offer canceled and funds returned"}), 200
    except Exception as e:
        print("Error while canceling offer:", e)
        return jsonify({"message": "Internal server error"}), 500

@app.route("/all_transactions", methods=['GET'])
@login_required
def all_transactions():
    try:
        all_transactions = list(transactions.find().sort("date", 1))
        for transaction in all_transactions:
            transaction['_id'] = str(transaction['_id'])
        return jsonify(all_transactions), 200
    except Exception as e:
        print(f"Błąd podczas pobierania transakcji: {e}")
        return jsonify({'error': 'Błąd podczas pobierania transakcji'}), 500


@app.route("/my_transactions", methods=['GET'])
@login_required
def my_transactions():
    user_email = current_user.email  # Fetching current logged-in user's email
    user_transactions = list(transactions.find({"from_user": user_email}).sort("date", 1))
    for transaction in user_transactions:
        transaction['_id'] = str(transaction['_id'])
    return jsonify(user_transactions), 200



if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)