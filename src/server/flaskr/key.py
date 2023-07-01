import functools
from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import rsa, padding
import json

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db
from .auth import login_required

bp = Blueprint('key', __name__, url_prefix='/key')

@bp.route('/publish', methods=('POST'))
@login_required
def publish(request):
    if request.method == 'POST':
        db = get_db()
        user_id = session.get("user_id")
        pubkey_entry = db.execute(
            "SELECT * FROM public_keys WHERE user_id = ?", user_id,
        ).fetchone()

        if pubkey_entry is not None:
            return "Public key already published"

        data = request.form['data']
        pubkey = request.form['pubkey']
        signature = request.form['signature']
        
        verified = pubkey.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        if verified:
            db.execute(
                "INSERT INTO user_public_keys (user_id, public_key) VALUES (?, ?)",
                (user_id, pubkey),
            )
            db.commit()
            return "Success"
        
        return "Signature verification failed"

@bp.route('/get/<int:user_id>', methods=('GET'))
@login_required
def get(user_id):
    if request.method == 'GET':
        db = get_db()
        pubkey_entry = db.execute(
            "SELECT * FROM public_keys WHERE user_id = ?", user_id,
        ).fetchone()

        if pubkey_entry is None:
            return "Public key not published"

        return pubkey_entry['public_key']
