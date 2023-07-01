"""
DATABASE QUERY FOR READ AND WRITE
"""

import sqlite3
from sqlite3 import Error

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
            self.conn = sqlite3.connect(FILE)
        except Error as exception:
            print(exception)
        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

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
        self.cursor.execute(
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
        self.cursor.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        )
        return self.cursor.fetchone()
    
    def get_user_by_id(self, user_id):
        """
        get a user from the db
        :param user_id: int
        :return: tuple
        """
        self.cursor.execute(
            'SELECT * FROM user WHERE id = ?',
            (user_id,)
        )
        return self.cursor.fetchone()
    
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
        self.cursor.execute(
            'UPDATE user SET public_key = ? WHERE id = ?',
            (public_key, user_id)
        )
        self.conn.commit()
    
    def get_public_key(self, username):
        """
        get a user's public key
        :param username: string
        :return: string
        """
        self.cursor.execute(
            'SELECT public_key FROM user WHERE username = ?',
            (username,)
        )
        return self.cursor.fetchone()['public_key']
    
    def get_group_id_by_name(self, group_name):
        """
        get a group's id
        :param group_name: string
        :return: int
        """
        self.cursor.execute(
            'SELECT id FROM gp WHERE name = ?',
            (group_name,)
        )
        return self.cursor.fetchone()['id']

    def create_group(self, user_id, group_name):
        """
        create a group
        :param user_id: int
        :param group_name: string
        :return: None
        """
        self.cursor.execute(
            'INSERT INTO gp (name, owner_id) VALUES (?, ?)',
            (group_name, user_id)
        )
        self.conn.commit()
    
    def is_admin(self, user_id, group_id):
        """
        check if a user is an admin of a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        self.cursor.execute(
            'SELECT user_role FROM gp_users WHERE gp_id = ? AND user_id = ?',
            (group_id, user_id)
        )
        user_role = self.cursor.fetchone()['user_role']
        return user_role == 'owner' or user_role == 'admin'
    
    def is_owner(self, user_id, group_id):
        """
        check if a user is the owner of a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        self.cursor.execute(
            'SELECT user_role FROM gp_users WHERE gp_id = ? AND user_id = ?',
            (group_id, user_id)
        )
        return self.cursor.fetchone()['user_role'] == 'owner'
    
    def add_user_to_group(self, user_id, group_id, user_role):
        """
        add a user to a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        self.cursor.execute(
            'INSERT INTO gp_users (gp_id, user_id, user_role) VALUES (?, ?, ?)',
            (group_id, user_id, user_role)
        )
        self.conn.commit()

    def get_group_users(self, group_id):
        """
        get all users in a group
        :param group_id: int
        :return: list
        """
        self.cursor.execute(
            'SELECT username FROM user WHERE id IN (SELECT user_id FROM gp_users WHERE gp_id = ?)',
            (group_id,)
        )
        return self.cursor.fetchall()
    
    def get_groups(self, user_id):
        """
        get all groups a user is in
        :param user_id: int
        :return: list
        """
        self.cursor.execute(
            'SELECT name FROM gp WHERE id IN (SELECT gp_id FROM gp_users WHERE user_id = ?)',
            (user_id,)
        )
        return self.cursor.fetchall()
    
    def delete_group(self, group_id):
        """
        delete a group
        :param group_id: int
        :return: None
        """
        self.cursor.execute(
            'DELETE FROM gp WHERE id = ?',
            (group_id,)
        )
        self.conn.commit()

    def is_member(self, user_id, group_id):
        """
        check if a user is a member of a group
        :param user_id: int
        :param group_id: int
        :return: bool
        """
        self.cursor.execute(
            'SELECT * FROM gp_users WHERE gp_id = ? AND user_id = ?',
            (group_id, user_id)
        )
        return self.cursor.fetchone() is not None
    
    def make_admin(self, user_id, group_id):
        """
        make a user an admin of a group
        :param user_id: int
        :param group_id: int
        :return: None
        """
        self.cursor.execute(
            'UPDATE gp_users SET user_role = ? WHERE gp_id = ? AND user_id = ?',
            ('admin', group_id, user_id)
        )
        self.conn.commit()