import os
import fnmatch
import zipfile

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from db import Comic
import settings

class Importer(object):
    def locate(self, pattern, root=os.curdir):
        for path, dirs, files in os.walk(os.path.abspath(root)):
            for filename in fnmatch.filter(files, pattern):
                yield os.path.join(path, filename)

    def addcomics(self, pattern, root, collection=""):
        for comic in self.locate(pattern, root):
            name = os.path.splitext(os.path.basename(comic))[0]
            self.addComic(title=name,
                          path=comic,
                          collection=collection)

    def cleanTmpDir(self, user):
        import shutil

        shutil.rmtree('tmp')
        os.mkdir('tmp')

    def addComic(self, title, path, user, collection=""):
        new_comic = Comic(title = title,
                          path = path,
                          collection = collection)
        new_comic.save()

        self.cleanTmpDir(user)

        splitfile = os.path.splitext(new_comic.path)
        if splitfile[1] == '.cbr':
            cmd = r'unrar e "%s" tmp/%s' % (new_comic.path, user)
            os.system(cmd)
            files = os.listdir('tmp')
            files.sort()
        else:
            try:
                z = zipfile.ZipFile(file(new_comic.path))
                z.extractall('tmp')
                files=z.namelist()
            except zipfile.BadZipfile:
                return

        cleanfiles = []
        for filename in files:
            if os.path.isfile('tmp/' + filename):
                cleanfiles.append(filename)

        new_comic.page_count = len(cleanfiles)
        new_comic.save()

        for pic, filename in zip(cleanfiles, new_comic.image_filenames(new_comic.id, new_comic.page_count)):
            s3conn = S3Connection(settings.S3_ID, settings.S3_KEY)
            bucket = s3conn.create_bucket(settings.S3_BUCKET)

            k = Key(bucket)
            k.key = filename
            k.set_contents_from_filename('tmp/'+pic, policy='public-read')

def main():
    """ Usage:
    python importer.py /path/to/comics [Collection Name]
    """

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
