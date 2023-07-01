from db import DataBase
from db import FILE as DB_FILE

import os
from flask import Flask, g, url_for
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
app.config['DATABASE'] = os.path.join(app.instance_path, DB_FILE)

db = DataBase()
socketio = SocketIO(app)

with app.app_context():
    g.db = db



from auth import bp as auth_bp
from user import bp as user_bp
from group import bp as group_bp

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(group_bp)


@app.route('/')
def home():
    return 'ok', 200






if __name__ == '__main__':
    socketio.run(app, debug=True)