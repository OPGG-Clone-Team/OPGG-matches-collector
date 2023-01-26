from pymongo import MongoClient
import os

host = os.getenv("MONGO_HOST")
port = int(os.getenv("MONGO_PORT"))
username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")


mongoClient = MongoClient(
  host=host,
  port=port,
  username=username,
  password=password,
)

def clear(database, clearCollectionList=[]):
  
  if len(clearCollectionList)!=0:
    for collection in clearCollectionList:
      mongoClient[database][collection].delete_many({})
  
  else:
    for collection in mongoClient[database].list_collection_names():
      mongoClient[database][collection].delete_many({})
