from flask import (
    Blueprint, g, session, url_for, request
)

from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from __main__ import socketio, db

bp = Blueprint('group', __name__, url_prefix='/group')

@bp.route('/create', methods=('POST',))
def create_group():
    """
    create a group
    :return: None
    """
    data = request.get_json()
    group_name = data['group_name']
    user_id = g.user['id']
    db.create_group(user_id, group_name)
    group_id = db.get_group_id_by_name(group_name)
    g.dp.add_user_to_group(user_id, group_name, user_role='owner')
    return "Group created successfully", 200

@bp.route('/invite_user', methods=('POST',))
def invite_user():
    """
    invite a user to a group
    :return: None
    """
    data = request.get_json()
    admin_id = g.user['id']
    group_name = data['group_name']
    user_id = data['user_id']

    if not db.is_admin(admin_id, group_name):
        return "You are not an admin of this group", 400
    else:
        db.add_user_to_group(user_id, group_name, user_role='member')
        return "User invited successfully", 200
    
@bp.route('/group_users/<string:group_name>', methods=('GET',))
def get_group_users(group_name):
    """
    get a list of users in a group
    :return: None
    """
    group_id = db.get_group_id_by_name(group_name)
    group_users = db.get_group_users(group_id)
    return group_users, 200

@bp.route('/get_groups', methods=('GET',))
def get_groups():
    """
    get a list of groups that a user is in
    :return: None
    """
    user_id = g.user['id']
    groups = db.get_groups(user_id)
    return groups, 200

@bp.route('/delete_group/<string:group_name>', methods=('DELETE',))
def delete_group(group_name):
    """
    delete a group
    :return: None
    """
    user_id = g.user['id']
    group_id = db.get_group_id_by_name(group_name)
    if not db.is_admin(user_id, group_id):
        return "You are not an admin of this group", 400
    else:
        db.delete_group(group_id)
        return "Group deleted successfully", 200

@bp.route('/leave_group/<string:group_name>', methods=('DELETE',))
def leave_group(group_name):
    """
    leave a group
    :return: None
    """
    user_id = g.user['id']
    group_id = db.get_group_id_by_name(group_name)
    if not db.is_member(user_id, group_id):
        return "You are not a member of this group", 400
    else:
        db.leave_group(user_id, group_id)
        return "Group left successfully", 200
    
@bp.route('make_admin', methods=('POST',))
def make_admin(group_name):
    """
    make a user an admin of a group
    :return: None
    """
    data = request.get_json()
    owner_id = g.user['id']
    user_id = data['user_id']
    group_name = data['group_name']
    group_id = db.get_group_id_by_name(group_name)

    if not db.is_owner(owner_id, group_id):
        return "You are not an owner of this group", 400
    else:
        db.make_admin(user_id, group_id)
        return "User made admin successfully", 200