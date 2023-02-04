# 상위 경로 패키지 로드
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 추후 환경변수 로드하는 공통로직 분리하기
from config.mongo import mongoClient
from riot_requests import match_v4
from decorator.trycatch_wrapper import trycatch



@trycatch
def update(app, matchId):
  db = mongoClient(app).LEAGUEDATA
  
  # DB에 match info가 이미 존재하면 업데이트 안함
  if db.matches.find_one({"matchId":matchId}):
    raise Exception("이미 전적 정보가 존재합니다.")
  
  match_info = match_v4.getMatchAndTimeline(matchId)
  
  if not match_info:
    raise Exception("매치정보를 찾는 데 실패했습니다.")
  
  db.matches.insert_one(match_info["match"])
  db.teams.insert_many(match_info["teams"])
  db.participants.insert_many(match_info["participants"])
  db.timelines.insert_many(match_info["timelines"])  
  print("매치정보를 모두 저장했습니다.")
  
  return match_info
  
if __name__=="__main__":
  update("KR_6336134778")
    
