from flask import (
    Blueprint, g, session, url_for, request
)


import os

from flask_socketio import join_room, leave_room
from __main__ import socketio, db, authenticated_only
from flask_login import login_required, current_user
from models import User

from validation.user import validate_request_json, validate_value

bp = Blueprint('user', __name__, url_prefix='/user')

online_users = set()

@login_required
@bp.route('/publish_key', methods=('POST',))
def publish_key():
    """
    publish a user's public key
    :return: None
    """
    user_id = current_user.get_id()
    public_key = request.data
    # if not validate_value(str(public_key, encoding='utf-8'), 'public_key'):
    #     return 'Invalid public key', 400
    try:
        if not db.user_exists(user_id):
            return 'User not found', 404
        elif db.user_has_public_key(user_id):
            return 'User already has a public key', 400
        db.save_public_key(user_id, public_key)
    except:
        return 'Internal server error', 500
    finally:
        return 'Public key published', 200

    

@bp.route('/get_public_key', methods=('POST',))
def get_public_key():
    """
    get a user's public key
    :return: None
    """
    data = request.get_json()
    if not validate_request_json(data, 'get_public_key'):
        return 'Invalid request format', 400
    username = data['username']
    if not validate_value(username, 'username'):
        return 'Invalid username', 400
    try:
        if not db.username_exists(username):
            return 'User not found', 404
        user_id = db.get_user_id_by_username(username)
        if not db.user_has_public_key(user_id):
            return 'User has no public key', 404
        public_key = db.get_user_public_key(user_id)
    except:
        return 'Internal server error', 500
    return public_key, 200

@bp.route('/get_online_users', methods=('GET',))
def get_online_users():
    """
    get a list of online users
    :return: None
    """
    return list(online_users), 200



@socketio.on('connect')
def connect():
    """
    handle the connect event
    :return: None
    """
    name = 'Anonymous'
    if current_user.is_authenticated:
        username = current_user.username
        online_users.add(username)
        join_room(username)
        name = username
    print(name + ' Connected.')

@socketio.on('disconnect')
def disconnect():
    """
    handle the disconnect event
    :return: None
    """
    name = 'Anonymous'
    if current_user.is_authenticated:
        username = current_user.username
        leave_room(username)
        online_users.remove(username)
        name = username
    print(name + ' Disconnected.')



@socketio.on('send_message')
@authenticated_only
def send_message(data):
    """
    handle the send_message event
    :return: None
    """
    username = current_user.username
    room = data['room']
    message = data['message']
    data_to_send = {
        'sender': username,
        'message': message,
        'room': room
    }
    socketio.emit('receive_message', data_to_send, room=room)

@socketio.on('join')
@authenticated_only
def on_join(data):
    """
    handle the join event
    :return: None
    """
    username = current_user.username
    room = data['room']
    join_room(room)
    socketio.emit('join', username + ' has entered the room.', room=room)
    print(username + ' joined room ' + room)

@socketio.on('leave')
@authenticated_only
def on_leave(data):
    """
    handle the leave event
    :return: None
    """
    username = current_user.username
    room = data['room']
    leave_room(room)
    socketio.emit('leave', username + ' has left the room.', room=room)

@socketio.on('logged_in')
@authenticated_only
def logged_in(data):
    """
    handle the logged_in event
    :return: None
    """
    print(current_user)
    username = current_user.username
    online_users.add(username)
    join_room(username)
    print(username + ' logged in.')
    socketio.emit('logged_in', username + ' has logged in.', room=username)

@socketio.on('logged_out')
@authenticated_only
def logged_out(data):
    """
    handle the logged_out event
    :return: None
    """
    username = current_user.username
    online_users.remove(username)
    leave_room(username)
    print(username + ' logged in.')
    socketio.emit('logged_out', username + ' has logged out.', room=username)