import functools

from flask import (
    Blueprint, g, session, url_for, request, redirect
)
from __main__ import db
from flask_socketio import join_room, leave_room
from flask_login import current_user, login_user, logout_user
from models import User
from validation.auth import validate_request_json, validate_value

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not validate_request_json(data, "register"):
        return 'Invalid request.', 400
    
    username = data['username']
    password = data['password']

    if not validate_value(username, "username"):
        return 'Invalid username.', 400
    elif not validate_value(password, "password"):
        return 'Invalid password.', 400
    else:
        try:
            db.save_user(username, password)
        except db.conn.IntegrityError:
            return f"User {username} is already registered.", 400
        else:
            return 'Registeration successful.', 200

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not validate_request_json(data, "register"):
        return 'Invalid request.', 400
    
    username = data['username']
    password = data['password']

    if not validate_value(username, "username"):
        return 'Invalid username.', 400
    elif not validate_value(password, "password"):
        return 'Invalid password.', 400
    else:
        try:
            user = db.get_user(username)
            if user is None:
                return 'Incorrect username.', 400
            elif not db.verify_password(username, password):
                return 'Incorrect password.', 400
            else:
                user_obj = User(user)
                login_user(user_obj)
        except:
            return 'Login failed.', 400
        else:
            return 'Login successful.', 200
            

@bp.route('/logout', methods=['POST'])
def logout():
    logout_user()
    return 'ok', 200
