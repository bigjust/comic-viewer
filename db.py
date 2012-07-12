import datetime

from pymongo import Connection
from mongoengine import *
from settings import DATABASE_NAME

import bcrypt

connection = Connection()
db = connection[DATABASE_NAME]
comics = db['comics']
users = db['users']

connect(DATABASE_NAME)

class Bookmark(Document):
    meta = {'collection': 'bookmarks'}
    user = StringField()
    comic = StringField()
    page = IntField(default=1)
    updated = DateTimeField()

    def __unicode__(self):
        return "<%s> Page %s" % (self.comic, self.page)

class Comic(Document):
    meta = {'collection': 'comics'}
    uploaded = DateTimeField(default=datetime.datetime.now)
    title = StringField()
    path = StringField()
    user = StringField()
    page_count = IntField(default=0)
    collection = StringField(default="None")

    @property
    def image_filenames(self):
        files = []

        for i in range(1, self.page_count + 1):
            seq = '%(num)03d' % {'num':i}
            filename = str(self.id) + '_' + seq + '.jpg'
            files.append(filename)

        return files

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
        return users.find_one({'username': username})

    def check_password(self, password):
        if bcrypt.hashpw(password, self.raw['password']) == self.raw['password']:
            return True
        return False

    def hash_password(self, password):
        self.raw['password'] = bcrypt.hashpw(password, bcrypt.gensalt(log_rounds=12))
        users.save(self.raw)
