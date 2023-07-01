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
