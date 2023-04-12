from flask import Flask, render_template, request
import poe
import time
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

conversation_history = []

def stream_gpt_response(conversation_text):
    token = poe.Account.create(logging=True)

    for response in poe.StreamingCompletion.create(
        model='gpt-4',
        prompt=conversation_text,
        token=token
    ):
        gpt_chunk = response.completion.choices[0].text
        emit("gpt_response_chunk", gpt_chunk)
    
    emit("gpt_response_complete")  # Add this line to signal completion

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('send_message')
def send_message(message):
    conversation_history.append(f"User: {message}")

    conversation_text = "\n".join(conversation_history)

    # Truncate conversation history to fit within the token limit
    max_tokens = 4096
    tokens = len(conversation_text)
    while tokens > max_tokens:
        conversation_history.pop(0)
        conversation_text = "\n".join(conversation_history)
        tokens = len(conversation_text)

    stream_gpt_response(conversation_text)

if __name__ == '__main__':
    socketio.run(app, debug=True)