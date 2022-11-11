from flask import Flask
from flask_pymongo import pymongo
from server import app

CONNECTION_STRING = "mongodb+srv://CurrentUser:AluxwYqUCVDmkhba@cluster0.gghbacw.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)

register_login_database = client.get_database('RegisterLoginDatabase')
forum_database = client.get_database('ForumDatabase')

user_collection = pymongo.collection.Collection(register_login_database, 'user_collection')
user_collection_2 = pymongo.collection.Collection(forum_database, 'user_collection')