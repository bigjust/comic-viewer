from bson.objectid import ObjectId

from db import users

class User(object):
    name = ''
    raw = None

    def __init__(self, user):
        if user:
            self.raw = user
            self.name = user['login']
            self.id = user['_id']

    def is_active(self):
        return True

    def get_id(self):
        return str(self.raw['_id'])

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_user(self):
        user = users.find_one({'login': ObjectId(id)})
        if not user:
            return None

        return user
