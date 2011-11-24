from pymongo import Connection

connection = Connection()
db = connection.test
comics = db['comics']
users = db['users']
