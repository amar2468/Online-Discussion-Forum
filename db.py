from flask import Flask
from flask_pymongo import pymongo
import app

CONNECTION_STRING = "mongodb+srv://CurrentUser:AluxwYqUCVDmkhba@cluster0.gghbacw.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)

forum_database = client.get_database('ForumDatabase')

user_collection_2 = pymongo.collection.Collection(forum_database, 'user_collection')