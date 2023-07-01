from flask import (
    Blueprint, g, session, url_for
)

from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import rsa, padding

socketio = g.socketio
bp = Blueprint('user', __name__, url_prefix='/user')

online_users = set()

@bp.route('/publish_key', methods= ('POST',))
def publish_key(request):
    """
    publish a user's public key
    :return: None
    """
    data = request.get_json()
    
    user_id = g.user['id']
    public_key = data['public_key']
    signature = data['signature']
    signed_data = data['signed_data']

    # verify the signature
    verified = public_key.verify(
        signature,
        signed_data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    if verified:
        g.db.save_public_key(user_id, public_key)
        return 'ok', 200
    else:
        return 'Verification failed', 400

@bp.route('/get_public_key', methods=('POST',))
def get_public_key(request):
    """
    get a user's public key
    :return: None
    """
    data = request.get_json()
    username = data['username']
    public_key = g.db.get_public_key(username)
    return public_key, 200

@bp.route('/get_online_users', methods=('GET',))
def get_online_users():
    """
    get a list of online users
    :return: None
    """
    return online_users, 200

@socketio.on('connect')
def connect(data):
    """
    handle the connect event
    :return: None
    """
    user_id = session.get('user_id')
    if user_id is not None:
        online_users.add(user_id)
    else:
        return False

@socketio.on('disconnect')
def disconnect():
    """
    handle the disconnect event
    :return: None
    """
    user_id = session.get('user_id')
    if user_id is not None:
        del online_users[user_id]
    else:
        return False