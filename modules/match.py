
from riot_requests import match_v4
import logging

# FIXME - pymongo insert operation 동작 시 원본 객체에 영향을 미치는 문제 발견
# https://pymongo.readthedocs.io/en/stable/faq.html#writes-and-ids
# _id까지 보내주는 dump_utils 사용하거나 다시 db에서 조회하는 방법으로 가야 할듯
# 우선은 직접 제거

logger = logging.getLogger("app")

def findOrUpdate(db, matchId):
  """
  특정 matchId로 match, teams, participants 업데이트 후 결과 반환

  Args:
      db (connection)
      matchId (str)

  Raises:
      Exception: _description_
      Exception: _description_
      
  Returns:
      matchInfo: {
        match,
        teams,
        participants
      }
  """
 
  # DB에 match info가 이미 존재하면 업데이트 안함
  match = db["matches"].find_one({"matchId":matchId}, {"_id":0})
  if match:
    # 2월 4일 수정 : 이미 있을 때는 DB에서 결과값 조회 후 반환
    
    teams = list(db["teams"].find({"matchId":matchId}, {"_id":0}))
    participants = list(db["participants"].find({"matchId":matchId}, {"_id":0}))
    timelines = list(db["participants"].find({"mathcId":matchId}, {"_id":0}))
    
    return {
      "match":match,
      "teams": teams,
      "participants":participants,
      "timelines":timelines
    }
    
  
  match_info = match_v4.getMatchAndTimeline(matchId)

  if not match_info:
    raise Exception("매치정보를 찾는 데 실패했습니다.")
  
  db["matches"].insert_one(match_info["match"],{})
  db["teams"].insert_many(match_info["teams"])
  db["participants"].insert_many(match_info["participants"])
  db["timelines"].insert_many(match_info["timelines"])
  
  # TODO 추후 다른 방안 고려하기
  # delete _id field 
  del(match_info["match"]["_id"])
  for team in match_info["teams"]:
    del(team["_id"])
  for participant in match_info["participants"]:
    del(participant["_id"])
  for timeline in match_info["timelines"]:
    del(timeline["_id"])
  
  return match_info
  
def findOrUpdateAll(db, matchId_list):
  result = []
  for matchId in matchId_list:
    result.append(findOrUpdate(db, matchId))
    
  return result
