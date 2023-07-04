"""
DATABASE QUERY FOR READ AND WRITE
"""

import sqlite3
from sqlite3 import Error
from threading import Lock

FILE = 'db.sqlite'
SCHEMA = 'schema.sql'

class DataBase:
    """
    used to connect, write to and read from a local sqlite3 database
    """

    def __init__(self):
        """
        try to connect to file and create cursor
        """
        self.conn = None
        try:
            self.conn = sqlite3.connect(FILE, check_same_thread=False)
        except Error as exception:
            print(exception)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()
        self.lock = Lock()

    def close(self):
        """
        close the db connection
        :return: None
        """
        self.conn.close()

    def init_db(self):
        with open(SCHEMA) as f:
            self.cursor.executescript(f.read())


    def save_user(self, username, password):
        """
        save a user to the db
        :param username: string
        :param password: string
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO user (username, password) VALUES (?, ?)',
                (username, password)
            )
            self.conn.commit()
    
    def get_user(self, username):
        """
        get a user from the db
        :param username: string
        :return: tuple
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT * FROM user WHERE username = ?',
                (username,)
            )
            return cursor.fetchone()
    
    def get_user_id_by_username(self, username):
        """
        get a user's id from the db
        :param username: string
        :return: int
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT id FROM user WHERE username = ?',
                (username,)
            )
            result =cursor.fetchone() 
            return result['id']

    
    def get_user_by_id(self, user_id):
        """
        get a user from the db
        :param user_id: int
        :return: tuple
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT * FROM user WHERE id = ?',
                (user_id,)
            )
            return cursor.fetchone()
    
    def get_username_by_id(self, user_id):
        """
        get a user's username from the db
        :param user_id: int
        :return: string
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT username FROM user WHERE id = ?',
                (user_id,)
            )
            return cursor.fetchone()['username']
    
    def user_exists(self, user_id):
        """
        check if a user exists
        :param user_id: int
        :return: bool
        """
        return self.get_user_by_id(user_id) is not None
    
    def username_exists(self, username):
        """
        check if a username exists
        :param username: string
        :return: bool
        """
        return self.is_username_taken(username)
    
    def is_username_taken(self, username):
        """
        check if a username is taken
        :param username: string
        :return: bool
        """
        return self.get_user_id_by_username(username) is not None

    
    def verify_password(self, username, password):
        """
        verify a user's password
        :param username: string
        :param password: string
        :return: bool
        """
        user = self.get_user(username)
        return user['password'] == password

    def save_public_key(self, user_id, public_key):
        """
        save a user's public key
        :param user_id: int
        :param public_key: string
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE user SET public_key = ? WHERE id = ?',
                (public_key, user_id)
            )
            self.conn.commit()
    
    def get_public_key_by_username(self, username):
        """
        get a user's public key
        :param username: string
        :return: string
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT public_key FROM user WHERE username = ?',
                (username,)
            )
            return cursor.fetchone()['public_key']
    
    def user_has_public_key(self, user_id):
        """
        check if a user has a public key
        :param user_id: int
        :return: bool
        """
        user = self.get_user_by_id(user_id)
        return user['public_key'] is not None
    
    def get_user_public_key(self, user_id):
        """
        get a user's public key
        :param user_id: int
        :return: string
        """
        user = self.get_user_by_id(user_id)
        return user['public_key']
    
    def get_group_by_name(self, group_name):
        """
        get a group by name
        :param group_name: string
        :return: tuple
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT * FROM gp WHERE name = ?',
                (group_name,)
            )
            return cursor.fetchone()
    
    def get_group_by_id(self, group_id):
        """
        get a group by id
        :param group_id: int
        :return: tuple
        """
        with self.conn:
            cursor = self.conn.cursor()
            print('-----')
            cursor.execute(
                'SELECT * FROM gp WHERE id = ?',
                (group_id,)
            )
            return cursor.fetchone()
    
    def get_group_id_by_name(self, group_name):
        """
        get a group's id by name
        :param group_name: string
        :return: int
        """
        group = self.get_group_by_name(group_name)
        return group['id']
    
    def get_group_owner_id(self, group_id):
        """
        get a group's owner id
        :param group_id: int
        :return: int
        """
        group = self.get_group_by_id(group_id)
        return group['owner_id']
        
    def is_group_name_taken(self, group_name):
        """
        check if a group name is already taken
        :param group_name: string
        :return: bool
        """
        return self.get_group_by_name(group_name) is not None


    def create_group(self, user_id, group_name):
        """
        create a group
        :param user_id: int
        :param group_name: string
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO gp (name, owner_id) VALUES (?, ?)',
                (group_name, user_id)
            )
            self.conn.commit()
    
    def add_user_to_group(self, user_id, group_id, user_role):
        """
        add a user to a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        print(user_id)
        print(group_id)
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'INSERT INTO gp_users (gp_id, user_id, user_role) VALUES (?, ?, ?)',
                (group_id, user_id, user_role)
            )
            self.conn.commit()

    def is_user_in_group(self, user_id, group_id):
        """
        check if a user is in a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT * FROM gp_users WHERE gp_id = ? AND user_id = ?',
                (group_id, user_id)
            )
            return cursor.fetchone() is not None

    def get_group_users(self, group_id):
        """
        get all users in a group
        :param group_id: int
        :return: list
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.row_factory = lambda cursor, row: row[0]
            cursor.execute(
                'SELECT username FROM user WHERE id IN (SELECT user_id FROM gp_users WHERE gp_id = ?)',
                (group_id,)
            )
            return cursor.fetchall()
    
    def get_user_groups(self, user_id):
        """
        get all groups a user is in
        :param user_id: int
        :return: list
        """
        with self.conn:
            cursor = self.conn.cursor()
            print(user_id)
            cursor.execute(
                # 'SELECT gp_id FROM gp_users WHERE user_id = ?',
                'SELECT name FROM gp WHERE id IN (SELECT gp_id FROM gp_users WHERE user_id = ?)',
                (user_id,)
            )
            cursor.row_factory = lambda cursor, row: row[0]
            return cursor.fetchall()
    
    def delete_group(self, group_id):
        """
        delete a group
        :param group_id: int
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM gp WHERE id = ?',
                (group_id,)
            )
            cursor.execute(
                'DELETE FROM gp_users WHERE gp_id = ?',
                (group_id,)
            )
            self.conn.commit()

    def remove_user_from_group(self, user_id, group_id):
        """
        remove a user from a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'DELETE FROM gp_users WHERE gp_id = ? AND user_id = ?',
                (group_id, user_id)
            )
            self.conn.commit()
    
    def set_role(self, user_id, group_id, role):
        """
        set a user's role in a group
        :param user_id: int
        :param group_id: int
        :param role: string
        :return: None
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'UPDATE gp_users SET user_role = ? WHERE gp_id = ? AND user_id = ?',
                (role, group_id, user_id)
            )
            self.conn.commit()
    
    def promote_user(self, user_id, group_id):
        """
        promote a user in a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        self.set_role(user_id, group_id, 'admin')
    
    def demote_user(self, user_id, group_id):
        """
        demote a user in a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        self.set_role(user_id, group_id, 'member')
    
    def get_role(self, user_id, group_id):
        """
        get a user's role in a group
        :param user_id: int
        :param group_id: int
        :return: string
        """
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                'SELECT user_role FROM gp_users WHERE gp_id = ? AND user_id = ?',
                (group_id, user_id)
            )
            role = cursor.fetchone()['user_role']
            print(role)
            return role
    
    def is_admin(self, user_id, group_id):
        """
        check if a user is an admin in a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        return self.get_role(user_id, group_id) == 'admin'
    
    def is_owner(self, user_id, group_id):
        """
        check if a user is the owner of a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        return self.get_group_by_id(group_id)['owner_id'] == user_id

    def is_member(self, user_id, group_id):
        """
        check if a user is a member of a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        return self.get_role(user_id, group_id) == 'member'
    
    def can_promote(self, user_id, group_id):
        """
        check if a user can promote other users in a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        return self.is_owner(user_id, group_id)

    def can_demote(self, user_id, group_id):
        """
        check if a user can demote other users in a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        return self.can_promote(user_id, group_id)
    
    def can_remove(self, remover_id, removee_id, group_id):
        """
        check if a user can remove another user from a group
        :param remover_id: int
        :param removee_id: int
        :param group_id: int
        :return: bool
        """
        if removee_id == remover_id:
            return False
        if self.is_owner(remover_id, group_id):
            return True
        if self.is_admin(remover_id, group_id) and self.is_member(removee_id, group_id):
            return True
        return False
    
