from pymongo import MongoClient
import os
import dotenv
from pymongo import IndexModel, ASCENDING, DESCENDING
          # >>> index1 = IndexModel([("hello", DESCENDING),
          # ...                      ("world", ASCENDING)], name="hello_world")
          # >>> index2 = IndexModel([("goodbye", DESCENDING)])
          # >>> db.test.create_indexes([index1, index2])

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


def create_initial_indexes():
  db = mongoClient.LEAGUEDATA
  
  # league_entries
  league_entries_index = IndexModel([
    ("summonerId",ASCENDING), 
    ("summonerName", ASCENDING)
    ], name ="league_entries_index")
  
  summoners_index = IndexModel([
    ("puuid", ASCENDING),
    ("name", ASCENDING)
  ], name = "summoners_index")
  
  summoner_matches_index = IndexModel([
    ("puuid", ASCENDING)
  ], name = "summoner_matches_index")
  
  matches_index = IndexModel([
    ("matchId", DESCENDING),
    ("gameCreation", DESCENDING),
  ], name = "matches_index")
  
  participants_index = IndexModel([
    ("matchId", DESCENDING),
    ("puuid", ASCENDING),
    ("teamId", ASCENDING),
  ],name = "participants_index")
  
  teams_index = IndexModel([
    ("matchId", DESCENDING),
    ("teamId", ASCENDING),
  ],name = "teams_index")
  
  db.league_entries.create_indexes([league_entries_index])
  db.summoners.create_indexes([summoners_index])
  db.summoner_matches.create_indexes([summoner_matches_index])
  db.matches.create_indexes([matches_index])
  db.participants.create_indexes([participants_index])
  db.temas.create_indexes([teams_index])
  
  
  

# TODO : 인덱스설정 등 초기설정은 추후 따로 분리할 것
create_initial_indexes()
# # db.league_entries.create('summonerName', unique = True,)


# def clear(database, clearCollectionList=[]):
  # """mongodb database 모두 삭제

  # Args:
  #     database (str): 삭제하려는 mongoDB 데이터베이스명
  #     clearCollectionList (list, optional): 비우려는 collection. 옵션을 주지 않으면 모든 콜렉션 비움
  # """
  
  # if len(clearCollectionList)!=0:
  #   for collection in clearCollectionList:
  #     mongoClient[database][collection].delete_many({})
  
  # else:
  #   for collection in mongoClient[database].list_collection_names():
  #     mongoClient[database][collection].delete_many({})
      