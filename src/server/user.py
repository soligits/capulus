from flask import (
    Blueprint, g, session, url_for
)

from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import rsa, padding

bp = Blueprint('user', __name__, url_prefix='/user')

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

