import unittest, sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from modules import league_entries, summoner
import dotenv
dotenv.load_dotenv(override=True)
# from config.mongo import mongoClient
from pymongo import MongoClient

class UnitTest(unittest.TestCase):
  '''
    전체 유저 batch (league_entries load + all summoner update)
  '''
  def setUp(self):
    self.db = MongoClient(
      host = os.getenv("MONGO_HOST"),
      username = os.getenv("MONGO_USERNAME"),
      password = os.getenv("MONGO_PASSWORD"),
    ).LEAGUEDATA
    self.db["league_entries"].find({})
    
  def test_update_all(self):
    league_entries.updateAll()
    print("league_entries 데이터 업데이트")
    
    league_entry_summoner = self.db["league_entries"].find({})
    for aSummoner in league_entry_summoner:
      summoner.updateBySummonerName(aSummoner["summonerName"])
      summoners = self.db["summoners"].find({})
    print("summoners 데이터 업데이트")      
      
    # league_entries의 summonerName을 돌려가면서 summoners안에 다 있는지 확인
    for aSummoner in league_entry_summoner:
      with self.assertRaises(Exception):
        self.db["summoners"].find_one({"name":aSummoner["summonerName"]})
        
    print("테스트 완료")   
    
if __name__ == '__main__':
  unittest.main()