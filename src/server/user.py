from flask import (
    Blueprint, g, session, url_for, request
)


import os

from flask_socketio import join_room, leave_room
from __main__ import socketio, db
from auth import login_required

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
    user_id = g.user['id']
    public_key = data['public_key']

    # verify the signature
    try :
        db.save_public_key(user_id, public_key)
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
def connect(data):
    """
    handle the connect event
    :return: None
    """
    print('Connected')

@socketio.on('disconnect')
def disconnect():
    """
    handle the disconnect event
    :return: None
    """
    print('Disconnected')

@socketio.on('login')
def login():
    """
    handle the login event
    :return: None
    """
    user_id = session.get('user_id')
    username = db.get_user_by_id(user_id)['username']
    room = username
    join_room(room)
    online_users.add(username)
    socketio.emit('login', username + ' has entered the room.', room=room)

@socketio.on('logout')
def logout():
    """
    handle the logout event
    :return: None
    """
    user_id = session.get('user_id')
    username = db.get_user_by_id(user_id)['username']
    room = username
    leave_room(room)
    online_users.remove(username)
    session.clear()
    socketio.emit('logout', username + ' has left the room.', room=room)

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