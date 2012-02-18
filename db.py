from datetime import datetime

from pymongo import Connection
from mongoengine import *
from settings import DATABASE_NAME

connection = Connection()
db = connection[DATABASE_NAME]
comics = db['comics']
users = db['users']

connect('cloudcomic')

class Comic(Document):
    meta = {'collection': 'comics'}
    uploaded = DateTimeField(default=datetime.now)
    title = StringField()
    path = StringField()
    user = StringField()
    page_count = IntField(default=0)
    read = BooleanField(default=False)
    collection = StringField(default="None")

    @property
    def image_filenames(self):
        files = []

        for i in range(1, self.page_count + 1):
            seq = '%(num)03d' % {'num':i}
            filename = str(id) + '_' + seq + '.jpg'
            files.append(filename)

        return files
