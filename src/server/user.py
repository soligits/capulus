from flask import (
    Blueprint, g, session, url_for, request
)


import os

from flask_socketio import join_room, leave_room
from __main__ import socketio, db, authenticated_only
from flask_login import login_required, current_user
from models import User

bp = Blueprint('user', __name__, url_prefix='/user')

online_users = set()

@login_required
@bp.route('/publish_key', methods= ('POST',))
def publish_key():
    """
    publish a user's public key
    :return: None
    """
    data = request.form
    user_id = current_user.get_id()
    public_key = data['public_key']

    # verify the signature
    try :
        db.save_public_key(user_id, public_key)
        current_user.public_key = public_key
        return 'ok', 200
    
    except :
        return 'Verification failed', 400

@bp.route('/get_public_key', methods=('POST',))
def get_public_key():
    """
    get a user's public key
    :return: None
    """
    data = request.get_json()
    username = data['username']
    public_key = db.get_public_key(username)
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
        del online_users[username]
        name = username
    print(name + ' Connected.')


@socketio.on('login')
@authenticated_only
def login():
    """
    handle the login event
    :return: None
    """
    user_id = current_user.get_id()
    username = current_user.username
    print(current_user)
    room = username
    join_room(room)
    online_users.add(username)
    # socketio.emit('login', username + ' has entered the room.', room=room)

@socketio.on('logout')
def logout():
    """
    handle the logout event
    :return: None
    """
    username = current_user['username']
    room = username
    leave_room(room)
    online_users.remove(username)
    # socketio.emit('logout', username + ' has left the room.', room=room)

@socketio.on('send_message')
def send_message(data):
    """
    handle the send_message event
    :return: None
    """
    username = data['username']
    room = data['room']
    message = data['message']
    socketio.emit('send_message', message, room=room)

@socketio.on('join')
def on_join(data):
    """
    handle the join event
    :return: None
    """
    username = data['username']
    room = data['room']
    join_room(room)
    socketio.emit('join', username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    """
    handle the leave event
    :return: None
    """
    username = data['username']
    room = data['room']
    leave_room(room)
    socketio.emit('leave', username + ' has left the room.', room=room)