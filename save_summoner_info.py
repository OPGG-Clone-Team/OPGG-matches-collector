import dotenv
dotenv.load_dotenv(override=True) # .env file 로드
import traceback

from customRequest import getSummonerMatches, getMatch
from mongo import mongoClient

db=mongoClient.LEAGUEDATA

summoner_name = "KT Way"

try:
  summoner = db.summoners.find_one({ "name" :summoner_name})
  
  if not summoner:
    raise Exception("유저를 찾을 수 없음")
  
  puuid =summoner["puuid"]
  
  old_summoner_matches = db.summoner_matches.find_one({"puuid":puuid})
  all_matches = set([]) # 모든 matchId 담을 변수
  
  if old_summoner_matches:
    all_matches.update(old_summoner_matches["summoner_match_ids"])
  
  # 1. customRequest - getSummonerMatches 호출
  new_summoner_match_Ids = getSummonerMatches(puuid)
  
  # 2. 리턴받은 데이터 저장
  if len(new_summoner_match_Ids) !=0:
    all_matches.update(new_summoner_match_Ids)
    
    filter = {'puuid':puuid}
    
    db.summoner_matches.update_one(filter, {"$set":{"summoner_match_ids":sorted(list(all_matches), reverse=True)}}, True) #Upsert:True
    print("소환사 매치아이디 리스트 저장 완료")   
    
    target_list = []
    
    # 갱신해야 할 데이터만 고르기
    if old_summoner_matches:
      target_list = list(all_matches-set(old_summoner_matches["summoner_match_ids"]))
    else:
      target_list = list(all_matches)
    
    # 매치데이터 생성 시작
    for match_id in sorted(target_list, reverse=True):
      print(f"matchId : {match_id}")
      
      # 1. match info 가져오기
      match_info = getMatch(match_id)
      
      if not match_info:
        continue
      
      # 2. matches collection에 정보 저장
      db.matches.update_one(
        {"matchId":match_id}, 
        {"$set":match_info["match"]}, True) #Upsert:True
      
      # 2-1. TeamID (100, 200)으로 구분된 Teams의 두 개의 객체에 대해서 teams collection(matchId 보유)에 저장 
      for team in match_info["teams"]:
        db.teams.update_one(
          {"matchId":team["matchId"], "teamId":team["teamId"]}, 
          {"$set":team}, True) #Upsert:True
        
      # 2-2. Participants의 10개의 객체에 대해서 participants collection(matchId, teamId 보유)에 저장
      for participant in match_info["participants"]:
        db.participants.update_one(
          {"matchId":participant["matchId"], "teamId":participant["teamId"], "puuid":participant["puuid"]}, 
          {"$set":participant}, True) #Upsert:True
      
      # 2-3. Timelines의 10개의 객체에 대해서 timelines collection(matchId, pariticipantId 보유)에 저장
      for timeline in match_info["timelines"]:
        db.timelines.update_one(
          {"matchId":timeline["matchId"], "participantId":timeline["participantId"], "puuid":timeline["puuid"]}, 
          {"$set":timeline}, True) #Upsert:True
      
except Exception as e:
  traceback.print_exc()
  