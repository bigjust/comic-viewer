from pymongo import Connection
from mongoengine import *
from settings import DATABASE_NAME

connection = Connection()
db = connection[DATABASE_NAME]
comics = db['comics']
users = db['users']

from boto.s3.connection import S3Connection
from boto.s3.key import Key

import settings

s3conn = S3Connection(settings.S3_ID, settings.S3_KEY)
bucket = s3conn.create_bucket(settings.S3_BUCKET)


import os
import fnmatch
from datetime import datetime
import zipfile

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


def generate_filenames(id, page_count):

        files = []

        for i in range(1, page_count + 1):
            seq = '%(num)03d' % {'num':i}
            filename = str(id) + '_' + seq + '.jpg'
            files.append(filename)

        return files


def cleanUserDir(user):
    import shutil

    shutil.rmtree('static/users/'+user)
    os.mkdir('static/users/'+user)


def addComic(title, path, user, collection=""):
    new_comic = Comic(title = title,
                      path = path,
                      user = user,
                      collection = collection)
    new_comic.save()

    cleanUserDir(user)

    splitfile = os.path.splitext(new_comic.path)
    if splitfile[1] == '.cbr':
        cmd = r'unrar e "%s" static/users/%s' % (new_comic.path, user)
        os.system(cmd)
        files = os.listdir('static/users/'+user)
        files.sort()
    else:
        try:
            z = zipfile.ZipFile(file(new_comic.path))
            z.extractall('static/users/'+user)
            files=z.namelist()
        except zipfile.BadZipfile:
            return

    cleanfiles = []
    for filename in files:
        if os.path.isfile('static/users/' + user + '/' + filename):
            cleanfiles.append(filename)

    new_comic.page_count = len(cleanfiles)
    new_comic.save()

    for pic, filename in zip(cleanfiles, generate_filenames(new_comic.id, new_comic.page_count)):
        k = Key(bucket)
        k.key = filename
        k.set_contents_from_filename('static/users/'+user+'/'+pic, policy='public-read')



class Importer(object):

    def locate(self, pattern, root=os.curdir):
        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)

    def addcomics(self, pattern, root, collection=""):
        for comic in self.locate(pattern, root):
            name = os.path.splitext(os.path.basename(comic))[0]
            if collection == "":
                collection = os.path.basename(os.path.dirname(comic))
            addComic(name,
                     comic,
                     'jcaratzas',
                     collection)


def main():
    import sys
    if (len(sys.argv) > 1):
        path = sys.argv[1]
    else:
        print "need atleast a path"
        return

    if (len(sys.argv) > 2):
        collection = ' '.join(sys.argv[2:])
    else:
        collection = ""

    importer = Importer()
    importer.addcomics("*.cbr", path, collection)
    importer.addcomics("*.cbz", path, collection)

if __name__ == '__main__':
    main()
