from pymongo import MongoClient
import os
import dotenv
dotenv.load_dotenv(override=True)


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
  """mongodb database 모두 삭제

  Args:
      database (str): 삭제하려는 mongoDB 데이터베이스명
      clearCollectionList (list, optional): 비우려는 collection. 옵션을 주지 않으면 모든 콜렉션 비움
  """
  
  if len(clearCollectionList)!=0:
    for collection in clearCollectionList:
      mongoClient[database][collection].delete_many({})
  
  else:
    for collection in mongoClient[database].list_collection_names():
      mongoClient[database][collection].delete_many({})
