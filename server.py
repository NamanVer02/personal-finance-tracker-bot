from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from bot import generate_response  # Import the chatbot function

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/chatbot', methods=['POST'])
@cross_origin()
def chatbot():
    # Get the request data
    request_data = request.json

    # Get the transactions data from the request body
    transactions_data = request_data.get('transactions')
    if not transactions_data:
        return jsonify({"error": "No transactions data provided"}), 400

    # Get the question from the request
    question = request_data.get('question')
    if not question:
        return jsonify({"error": "No question provided"}), 400

    # Generate a response using the chatbot
    response = generate_response(transactions_data, question)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)