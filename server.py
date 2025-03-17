from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import requests
from bot import generate_response  # Import the chatbot function

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Hardcoded credentials and URLs
LOGIN_URL = "http://localhost:8080/api/auth/signin"
TRANSACTIONS_URL = "http://localhost:8080/api/get/admin/transactions"
CREDENTIALS = {"username": "admin", "password": "admin"}

# Function to fetch transactions data
def fetch_transactions():
    try:
        # Step 1: Authenticate and get JWT token
        auth_response = requests.post(LOGIN_URL, json=CREDENTIALS)
        auth_response.raise_for_status()  # Raise an error for bad status codes
        token = auth_response.json().get('token')  # Assuming the token is returned in a 'token' field

        if not token:
            return None, "Authentication failed, no token received"

        # Step 2: Use the JWT token to fetch transactions
        headers = {"Authorization": f"Bearer {token}"}
        transactions_response = requests.get(TRANSACTIONS_URL, headers=headers)
        transactions_response.raise_for_status()

        # Step 3: Return the transactions JSON
        return transactions_response.json(), None

    except requests.exceptions.RequestException as e:
        return None, str(e)

@app.route('/')
@cross_origin()
def get_transactions():
    data, error = fetch_transactions()
    if error:
        return jsonify({"error": error}), 500
    return jsonify(data)

@app.route('/chatbot', methods=['POST'])
@cross_origin()
def chatbot():
    # Fetch the transactions data
    data, error = fetch_transactions()
    if error:
        return jsonify({"error": error}), 500

    # Get the question from the request
    question = request.json.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Generate a response using the chatbot
    response = generate_response(data, question)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)