import functools

from flask import (
    Blueprint, g, session, url_for
)

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=['POST'])
def register(request):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = g.db

        if not username:
            return 'Username is required.', 400
        elif not password:
            return  'Password is required.', 400
        else:
            try:
                db.save_user(username, password)
            except db.IntegrityError:
                return f"User {username} is already registered.", 400
            else:
                return 'ok', 200
    else:
        return 'Method not allowed.', 405

@bp.route('/login', methods=['POST'])
def login(request):
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = g.db

        if not username:
            return 'Username is required.', 400
        elif not password:
            return  'Password is required.', 400
        else:
            user = db.get_user(username)
            if user is None:
                return 'Incorrect username.', 400
            elif not db.verify_password(username, password):
                return 'Incorrect password.', 400
            else:
                session.clear()
                session['user_id'] = user['id']
                return 'ok', 200
    else:
        return 'Method not allowed.', 405

@bp.route('/logout', methods=['POST'])
def logout(request):
    if request.method == 'POST':
        session.clear()
        return 'ok', 200
    else:
        return 'Method not allowed.', 405

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    db = g.db

    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by_id(user_id)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return 'Unauthorized.', 401
        else:
            return view(**kwargs)
    return wrapped_view