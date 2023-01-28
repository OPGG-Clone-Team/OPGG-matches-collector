import requests
import os

def getSummonerMatches(puuid, start=0, count = 20):
  """
  유저의 최근 전적 id 리스트 가져오기
  2000 requests every 10 seconds

  Args:
      puuid (str)
      start (int, optional): 조회 시작 index, Defaults to 0.
      count (int, optional): 조회할 row 수, Defaults to 20.

  Returns:
      [matchIds]: 전적 id 리스트
  """
  
  queue = 420 # rank solo
  type = "ranked"
  
  url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&type={type}&start={start}&count={count}"
  
  print(f'다음으로 request : {url}')
  
  result = requests.get(url, headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json()
  
  return result


def getMatchAndTimeline(matchId):
  """
  특정한 매치 정보 가져오기
  2000 requests every 10 seconds
  2023/01/21 수정 : Return type 수정 (timeline)
  
  Args:
      matchId (str)

  Returns:
      {match,teams,participants, timelines}(Nullable)
  """
  
  if not matchId:
    return None
  
  url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}"
  
  print(f'다음으로 request : {url}')
  
  # 여기서부터는 필수 정보 제외하고 죄다 갖다 버리기
  
  result = requests.get(url, headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json()
  result_timeline = requests.get(url+'/timeline', headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json()
  
  # 코드 수정 : result와 result_timeline 둘 중 하나도 존재하지 않으면 return none
  if result.get("status") or result_timeline.get("status"):
    return None
  
  info = result["info"]
  info_teams = []
  info_participants = []
  
  
  # timeline에서 얻은 정보
  timelines = {}
  
  # timeline = {
  #   "matchId" : matchId,
  #   "puuid":puuid,
    
  #   "itemBuild":{},
  #   "skillBuild":[]
  # }
  
  match = {
    "matchId" : matchId,
    "gameCreation": info["gameCreation"],
    "gameDuration": info["gameDuration"],
    "queueId": info["queueId"]
  }
  
  for team in info["teams"]:
    info_teams.append({
      "matchId" : matchId,
      "teamId":team["teamId"],
      "win":team["win"],
      "bans":team["bans"],
      "baron":team["objectives"]["baron"]["kills"],
      "dragon":team["objectives"]["dragon"]["kills"],
      "tower":team["objectives"]["tower"]["kills"],
      "totalKills":team["objectives"]["champion"]["kills"],
    })
  
  for participant in info["participants"]:
    lane = participant["individualPosition"]
    if lane == "UTILITY":
      lane = "SUPPORT"
    
    challenges=participant["challenges"]
    
    info_participants.append({
      "matchId" : matchId,
      "teamId":participant["teamId"],
      "puuid":participant["puuid"],
      "totalDamageTaken":participant["totalDamageTaken"],
      "totalDamageDealtToChampions":participant["totalDamageDealtToChampions"],
      "wardsPlaced":participant["wardsPlaced"],
      "wardsKilled":participant["wardsKilled"],
      "visionWardsBoughtInGame":participant["visionWardsBoughtInGame"],
      "summonerLevel":participant["summonerLevel"],
      "championId":participant["championId"],
      "championName":participant["championName"],
      "kills":participant["kills"],
      "deaths":participant["deaths"],
      "lane":lane,
      "cs":int(participant["totalMinionsKilled"])+int(participant["neutralMinionsKilled"]),
      "killParticipation":challenges["killParticipation"],
      "goldEarned":participant["goldEarned"],
      "kda":str(round(float(challenges["kda"]),2)),
      "pentaKills":participant["pentaKills"],
      "quadraKills":participant["quadraKills"],
      "tripleKills":participant["tripleKills"],
      "doubleKills":participant["doubleKills"],
      "perks":participant["perks"],
      "item0":participant["item0"],
      "item1":participant["item1"],
      "item2":participant["item2"],
      "item3":participant["item3"],
      "item4":participant["item4"],
      "item5":participant["item5"],
      "item6":participant["item6"],
    })
  
  for initial_timeline_info in result_timeline["info"]["participants"]:
    timelines[initial_timeline_info["participantId"]]={
      "matchId":matchId,
      "puuid": initial_timeline_info["puuid"],
      "participantId":initial_timeline_info["participantId"],
      "itemBuild":{},
      "skillBuild":[]
    }
    
  frameCount=0 # frameInteval로 나눈 event frame
  for timeline_info in result_timeline["info"]["frames"]:
    for event in timeline_info["events"]:
      
      # 아이템 구매 내역, 스킬 레벨업 내역이 담긴 event만 추출
      if "type" in event and event["type"] in ["ITEM_PURCHASED","SKILL_LEVEL_UP"]:
        event_type = event["type"]
        participantId = event["participantId"]
        target_timeline = timelines[participantId]
        
        #1. 아이템 빌드 stack
        if event_type=="ITEM_PURCHASED":
          itemId = event["itemId"]
          
          # 이미 interval이 존재하는 경우
          if str(frameCount) in target_timeline["itemBuild"]:
            target_timeline["itemBuild"][str(frameCount)].append(itemId)
          # interval 신규 생성
          else:
            target_timeline["itemBuild"][str(frameCount)] = [itemId]
        
        #2. 스킬 빌드 stack
        elif event_type=="SKILL_LEVEL_UP":
          target_timeline["skillBuild"].append(event["skillSlot"])
    frameCount+=1
  
  return { "match" :match, "teams":info_teams, "participants":info_participants, "timelines":timelines.values() }