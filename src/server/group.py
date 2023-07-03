from flask import (
    Blueprint, g, request
)

from __main__ import db
from flask_login import login_required, current_user
from validation.group import validate_request_json, validate_value

bp = Blueprint('group', __name__, url_prefix='/group')

@login_required
@bp.route('/create', methods=('POST',))
def create_group():
    """
    create a group
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'create_group'):
        return "Invalid request format", 400
    
    group_name = data['group_name']
    user_id = current_user.get_id()
    if db.is_group_name_taken(group_name):
        return "Group name already taken", 400
    if not db.user_exists(user_id):
        return "User does not exist", 400
    
    try:
        db.create_group(user_id, group_name)
    except:
        return "Internal server error", 500

    try:
        db.add_user_to_group(user_id, group_name, user_role='admin')
    except:
        return "Internal server error", 500
    
    return "Group created successfully", 200

@login_required
@bp.route('/invite_user', methods=('POST',))
def invite_user():
    """
    invite a user to a group
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'invite_user'):
        return "Invalid request format", 400

    admin_id = current_user.get_id()
    group_name = data['group_name']
    username = data['username']


    try:
        if not db.username_exists(username):
            return "Username does not exist", 400
        user_id = db.get_user_id_by_username(username)
        if not db.is_admin(admin_id, group_name):
            return "You are not an admin of this group", 400
        elif db.is_user_in_group(user_id, group_name):
            return "User is already in this group", 400
        else:
            db.add_user_to_group(user_id, group_name, user_role='member')
    except:
        return "Internal server error", 500
    finally:
        return "User invited successfully", 200
        

@login_required
@bp.route('/remove_user', methods=('POST',))
def remove_user():
    """
    remove a user from a group
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'remove_user'):
        return "Invalid request format", 400

    admin_id = current_user.get_id()
    group_name = data['group_name']
    username = data['username']

    try:
        if not db.username_exists(username):
            return "Username does not exist", 400
        user_id = db.get_user_id_by_username(username)
        if not db.is_admin(admin_id, group_name):
            return "You are not an admin of this group", 400
        elif not db.is_user_in_group(user_id, group_name):
            return "User is not in this group", 400
        else:
            db.remove_user_from_group(user_id, group_name)
    except:
        return "Internal server error", 500
    finally:
        return "User removed successfully", 200

@login_required 
@bp.route('/group_users/<string:group_name>', methods=('GET',))
def get_group_users(group_name):
    """
    get all users in a group
    :return: None
    """
    if not validate_value(group_name, 'group_name'):
        return "Invalid group name", 400

    try:
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        users = db.get_group_users(group_name)
    except:
        return "Internal server error", 500
    finally:
        return users, 200

@login_required
@bp.route('/get_groups', methods=('GET',))
def get_groups():
    """
    get all groups a user is in
    :return: None
    """
    try:
        user_id = current_user.get_id()
        groups = db.get_groups(user_id)
    except:
        return "Internal server error", 500
    finally:
        return groups, 200

@login_required
@bp.route('/delete_group', methods=('POST',))
def delete_group():
    """
    delete a group
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'delete_group'):
        return "Invalid request format", 400

    admin_id = current_user.get_id()
    group_name = data['group_name']

    try:
        if not db.is_admin(admin_id, group_name):
            return "You are not an admin of this group", 400
        db.delete_group(group_name)
    except:
        return "Internal server error", 500
    finally:
        return "Group deleted successfully", 200

@login_required
@bp.route('/leave_group', methods=('POST',))
def leave_group():
    """
    leave a group
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'leave_group'):
        return "Invalid request format", 400

    user_id = current_user.get_id()
    group_name = data['group_name']

    try:
        if not db.is_user_in_group(user_id, group_name):
            return "You are not in this group", 400
        db.remove_user_from_group(user_id, group_name)
    except:
        return "Internal server error", 500
    finally:
        return "Group left successfully", 200

@login_required
@bp.route('/promote_user', methods=('POST',))
def promote_user():
    """
    promote a user to admin
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'promote_user'):
        return "Invalid request format", 400

    owner_id = current_user.get_id()
    group_name = data['group_name']
    username = data['username']

    try:
        if not db.username_exists(username):
            return "Username does not exist", 400
        user_id = db.get_user_id_by_username(username)
        if not db.can_promote(owner_id, group_name):
            return "You are not an owner of this group", 400
        elif not db.is_user_in_group(user_id, group_name):
            return "User is not in this group", 400
        elif db.is_admin(user_id, group_name):
            return "User is already an admin", 400
        else:
            db.promote_user(user_id, group_name)
    except:
        return "Internal server error", 500
    finally:
        return "User promoted successfully", 200

@login_required
@bp.route('/demote_user', methods=('POST',))
def demote_user():
    """
    demote a user from admin
    :return: None
    """
    data = request.get_json()
    # check data format
    if not validate_request_json(data, 'demote_user'):
        return "Invalid request format", 400

    owner_id = current_user.get_id()
    group_name = data['group_name']
    username = data['username']

    try:
        if not db.username_exists(username):
            return "Username does not exist", 400
        user_id = db.get_user_id_by_username(username)
        if not db.can_demote(owner_id, group_name):
            return "You are not an owner of this group", 400
        elif not db.is_user_in_group(user_id, group_name):
            return "User is not in this group", 400
        elif not db.is_admin(user_id, group_name):
            return "User is not an admin", 400
        else:
            db.demote_user(user_id, group_name)
    except:
        return "Internal server error", 500
    finally:
        return "User demoted successfully", 200

