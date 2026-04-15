import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_chat_key_123'
# logger=True helps you see connection issues in the Render logs
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

def init_db():
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS messages 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       username TEXT, message TEXT, color TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    init_db() # Ensures table exists every time someone visits
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT username, message, color FROM messages ORDER BY id ASC")
        history = cursor.fetchall()
    except sqlite3.OperationalError:
        history = []
    conn.close()
    return render_template('index.html', history=history)

@socketio.on('send_message')
def handle_message(data):
    conn = sqlite3.connect('chat.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (username, message, color) VALUES (?, ?, ?)", 
                   (data['username'], data['message'], data.get('color', '#ffffff')))
    conn.commit()
    conn.close()
    emit('receive_message', data, broadcast=True)

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=False)
