from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot import get_response

app = Flask(__name__, template_folder="template")
CORS(app)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    # Retrieve the user's message from the request
    user_message = request.json['message']

    # Get the chatbot's response
    bot_response = get_response(user_message)

    # Return the chatbot's response to the user
    return jsonify({'message': bot_response})

if __name__ == '__main__':
    app.run(debug=True)
