from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow CORS for all routes

# Define the route for handling incoming messages
@app.route('/api/process_message', methods=['POST'])
def process_message():
    data = request.get_json()
    messages = data['messages']
    print(data)
    
    if messages:
        response_message = f"You said: {messages[-1]}"
    else:
        response_message = "No message received."

    response = {
        "message": response_message
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
