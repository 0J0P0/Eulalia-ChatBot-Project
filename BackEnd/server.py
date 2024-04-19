from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Define the route for handling incoming messages
@app.route('/api/process_message', methods=['POST'])
def process_message():
    # Extract the messages from the JSON payload
    data = request.get_json()
    # print(data)
    messages = data['messages']
    # print(messages)
    # Here you can process the messages (e.g., send to ChatGPT)
    # For simplicity, we'll echo back the last message received
    if messages:
        response_message = f"You said: {messages[-1]}"
    else:
        response_message = "No message received."

    # Create a response JSON with the processed message
    response = {
        "message": response_message
    }

    # Send the response back to the frontend
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
