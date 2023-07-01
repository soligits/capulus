from db import DataBase
from db import FILE as DB_FILE

import os
from flask import Flask, g
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config['DATABASE'] = os.path.join(app.instance_path, DB_FILE)

db = DataBase()
socketio = SocketIO(app)
with app.app_context():
    g.socketio = socketio
    g.db = db

@app.route('/')
def home():
    return 'ok', 200





if __name__ == '__main__':
    socketio.run(app, debug=True)