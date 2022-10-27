from flask import Flask
from flask_pymongo import pymongo
from server import app

CONNECTION_STRING = "mongodb+srv://CurrentUser:AluxwYqUCVDmkhba@cluster0.gghbacw.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('RegisterLoginDatabase')
user_collection = pymongo.collection.Collection(db, 'user_collection')