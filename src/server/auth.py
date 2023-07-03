import functools

from flask import (
    Blueprint, g, session, url_for, request, redirect
)
from __main__ import db
from flask_socketio import join_room, leave_room
from flask_login import current_user, login_user, logout_user
from models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':

        username = request.json['username']
        password = request.json['password']

        if not username:
            return 'Username is required.', 400
        elif not password:
            return  'Password is required.', 400
        else:
            try:
                db.save_user(username, password)
            except db.conn.IntegrityError:
                return f"User {username} is already registered.", 400
            else:
                return 'ok', 200
    else:
        return 'Method not allowed.', 405

@bp.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']

        if not username:
            return 'Username is required.', 400
        elif not password:
            return  'Password is required.', 400
        else:
            user = db.get_user(username)
            user_obj = User(user)
            if user is None:
                return 'Incorrect username.', 400
            elif not db.verify_password(username, password):
                return 'Incorrect password.', 400
            else:
                login_user(user_obj)

                return 'ok', 200
    else:
        return 'Method not allowed.', 405

@bp.route('/logout', methods=['POST'])
def logout():
    if request.method == 'POST':
        logout_user()
        return 'ok', 200
    else:
        return 'Method not allowed.', 405

# @bp.before_app_request
# def load_logged_in_user():

#     user_id = session.get('user_id')

#     print(user_id)


#     if user_id is None:
#         g.user = None
#     else:
#         g.user = db.get_user_by_id(user_id)

# def login_required(view):
#     @functools.wraps(view)
#     def wrapped_view(**kwargs):
#         if g.user is None:
#             return 'Unauthorized.', 401
#         else:
#             return view(**kwargs)
#     return wrapped_view