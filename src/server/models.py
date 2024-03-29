from flask_login import UserMixin

class User(UserMixin):
    all_users = {}

    def __init__(self, user):
        self.id = user['id']
        self.username = user['username']
        self.password = user['password']
        self.public_key = user['public_key']

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def get_id(self):
        return self.id
    
    