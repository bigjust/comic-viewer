import bcrypt

from db import users

class User(object):
    username = ''
    raw = {}

    def __init__(self, username):
        if username:
            self.username=username

        self.raw = self.get_user(username)

        if self.raw is None:
            return None

    def is_active(self):
        return True

    def get_id(self):
        return str(self.raw['_id'])

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_user(self, username):
        return users.find_one({'login': username})

    def check_password(self, password):
        if bcrypt.hashpw(password, self.raw['password']) == self.raw['password']:
            return True
        return False

    def hash_password(self, password):
        self.raw['password'] = bcrypt.hashpw(password, bcrypt.gensalt(log_rounds=12))
        users.save(self.raw)
