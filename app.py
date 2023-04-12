from flask import Flask, request, jsonify
from flask_cors import CORS
import your_chat_script  # Import your existing Python chat script

app = Flask(__name__)
CORS(app)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.json['message']
    response = your_chat_script.send_message(message)  # Call the send_message function from your Python chat script
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True)