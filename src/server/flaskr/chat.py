import functools


from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from flaskr.db import get_db
from .auth import login_required

bp = Blueprint('chat', __name__, url_prefix='/chat')

@bp.route('/online', methods=('GET'))
@login_required
def online(request):
    if request.method == 'GET':
        return list(g.online_users.keys())

@bp.route
