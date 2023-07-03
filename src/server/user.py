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
        print(public_key)
        print(user_id)
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
        online_users.remove(username)
        name = username
    print(name + ' Connected.')



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

@socketio.on('online')
@authenticated_only
def on_online(data):
    """
    handle the online event
    :return: None
    """
    username = current_user.username
    online_users.add(username)

@socketio.on('offline')
@authenticated_only
def on_offline(data):
    """
    handle the offline event
    :return: None
    """
    username = current_user.username
    online_users.remove(username)