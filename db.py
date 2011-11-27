from pymongo import Connection
from settings import DATABASE_NAME

connection = Connection()
db = connection[DATABASE_NAME]
comics = db['comics']
users = db['users']
