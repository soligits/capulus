from flask import (
    Blueprint, g, request
)

from __main__ import db, authenticated_only, socketio
from flask_login import login_required, current_user
from flask_socketio import join_room, leave_room
from validation.group import validate_request_json, validate_value

bp = Blueprint('group', __name__, url_prefix='/group')

@login_required
@bp.route('/create_group', methods=('POST',))
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
        group_id = db.get_group_id_by_name(group_name)
        db.add_user_to_group(user_id, group_id, user_role='admin')
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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        if not db.is_admin(admin_id, group_id) and not db.is_owner(admin_id, group_id):
            return "You are not an admin of this group", 400
        elif db.is_user_in_group(user_id, group_id):
            return "User is already in this group", 400
        else:
            db.add_user_to_group(user_id, group_id, user_role='member')
            return "User invited successfully", 200
    except:
        return "Internal server error", 500
        

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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        if not db.is_admin(admin_id, group_id):
            return "You are not an admin of this group", 400
        elif not db.is_user_in_group(user_id, group_id):
            return "User is not in this group", 400
        else:
            db.remove_user_from_group(user_id, group_id)
            return "User removed successfully", 200
    except:
        return "Internal server error", 500

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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        users = db.get_group_users(group_id)
        return users, 200
    except:
        return "Internal server error", 500

@login_required
@bp.route('/get_groups', methods=('GET',))
def get_groups():
    """
    get all groups a user is in
    :return: None
    """
    try:
        user_id = current_user.get_id()
        groups = db.get_user_groups(user_id)
        return groups, 200
    except Exception as e:
        return "Internal server error", 500

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

    owner_id = current_user.get_id()
    group_name = data['group_name']

    try:
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        if not db.is_owner(owner_id, group_id):
            return "You are not an owner of this group", 400
        db.delete_group(group_id)
        return "Group deleted successfully", 200
    except:
        return "Internal server error", 500

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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        if not db.is_user_in_group(user_id, group_id):
            return "You are not in this group", 400
        if db.is_owner(user_id, group_id):
            return "You are the owner of this group, you cannot leave", 400
        db.remove_user_from_group(user_id, group_id)
        return "Group left successfully", 200
    except:
        return "Internal server error", 500

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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        print(user_id)
        print(group_id)
        if not db.can_promote(owner_id, group_id):
            return "You are not an owner of this group", 400
        elif not db.is_user_in_group(user_id, group_id):
            return "User is not in this group", 400
        elif db.is_admin(user_id, group_id):
            return "User is already an admin", 400
        else:
            db.promote_user(user_id, group_id)
            return "User promoted successfully", 200
    except:
        return "Internal server error", 500

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
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        print(user_id)
        print(group_id)
        if not db.can_demote(owner_id, group_id):
            return "You are not an owner of this group", 400
        elif not db.is_user_in_group(user_id, group_id):
            return "User is not in this group", 400
        elif not db.is_admin(user_id, group_id):
            return "User is not an admin", 400
        else:
            db.demote_user(user_id, group_id)
    except:
        return "Internal server error", 500
    return "User demoted successfully", 200

@login_required
@bp.route('/get_group_owner', methods=('POST',))
def get_group_owner():
    """
    get the owner of a group
    :return: owner username
    """
    data = request.get_json()
    # check data format
    # if not validate_request_json(data, 'get_group_owner'):
    #     return "Invalid request format", 400

    group_name = data['group_name']

    try:
        if not db.is_group_name_taken(group_name):
            return "Group does not exist", 400
        group_id = db.get_group_id_by_name(group_name)
        print(group_id)
        owner_id = db.get_group_owner_id(group_id)
        print(owner_id)
        owner_username = db.get_username_by_id(owner_id)
        return owner_username, 200
    except Exception as e:
        print(e)
        return "Internal server error", 500


@socketio.on('join_group_chat')
@authenticated_only
def join_group_chat(data):
    group_name = data['group_name']
    room_name = '%' + group_name
    join_room(room_name)
    username = current_user.username
    message = username + ' joined group room ' + group_name
    socketio.emit('join_group_chat', {'message': message, 'group_name': group_name, 'username': username}, to=room_name)

@socketio.on('leave_group_chat')
@authenticated_only
def leave_group_chat(data):
    group_name = data['group_name']
    room_name = '%' + group_name
    leave_room(room_name)
    username = current_user.username
    message = username + ' left group room ' + group_name
    socketio.emit('leave_group_chat', {'message': message, 'group_name': group_name, 'username': username}, to=room_name)

@socketio.on('send_group_message')
@authenticated_only
def send_group_message(data):
    group_name = data['group_name']
    room_name = '%' + group_name
    message = data['message']
    username = current_user.username
    socketio.emit('receive_group_message', {'message': message, 'sender': username, 'group_name': group_name}, room=room_name)