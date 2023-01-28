import requests
import os

def get_specific_league(tier, queue="RANKED_SOLO_5x5"):
  """
  해당 tier에 존재하는 모든 소환사 정보 가져오기\n
  50 requests every 10 seconds

  Args:
      tier (str, required): should be in ["challengerleagues", "grandmasterleagues","masterleagues"].
      queue (str, optional): 조회할 큐 선택, Defaults to "RANKED_SOLO_5x5".

  Returns:
      [LeagueListDTO]: {
        freshBlood (boolean) : 아직 뭔지모름,
        wins (int),
        summonerName (string),
        miniSeries (MiniSeriesDTO),
        inactive (boolean) : 아직 뭔지모름,
        veteran	(boolean) : 아직 뭔지모름,
        hotStreak	(boolean) : 아직 뭔지모름,	
        rank (string): 세부 티어 (ex: Diamond 1 -> rank : "I"),
        leaguePoints (int) 점수,	
        losses (int),
        summonerId (string),
      }
  """
  if tier not in ["challengerleagues", "grandmasterleagues","masterleagues"]:
    return []
  
  url = f"https://kr.api.riotgames.com/lol/league/v4/{tier}/by-queue/{queue}"

  # 추후 logging 적용
  print(f'다음으로 request : {url}')

  result = requests.get(url, headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}).json() ## list type expected
  
  entries = result["entries"]
  
  # 만약 list데이터로 넘어오지 않는다면 (ERROR 발생) response 출력 후 함수 종료
  # fetching한 데이터가 비어 있으면 함수 즉시 종료
  if not entries or not isinstance(entries, list):
    print(result)
    return []

  return entries

# def getSummoner(id):
#   """
#   summonerId로 Summoner 정보 가져오기\n
#   1600 requests every 1 minutes\n
#   경고 - Consistently looking up summoner ids that don't exist will result in a blacklist.\n
  
#   Args:
#       id (str): summonerId

#   Returns:
#       Summoner: {
#         "id": 소환사 ID,
#         "accountId": 소환사 계정 ID,
#         "puuid": 소환사 PUUID,
#         "name": 소환사명,
#         "profileIconId": 프로필 아이콘 id,
#         "revisionDate": 소환사 정보 최종 수정일,
#         "summonerLevel": 소환사 레벨,
#         "queryAllowTime": 해당 소환사를 query 가능한 시간, default : null
#       }
#   """
  
#   url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{id}"

#   # 추후 logging 적용
#   print(f'다음으로 request : {url}')
#   result = requests.get(url, headers={"X-Riot-Token":API_KEY}).json()
  
#   if "id" not in result:
#     return {}
  
#   return result

# def getSummonerMatches(puuid, start=0, count = 20):
#   """
#   유저의 최근 전적 id 리스트 가져오기
#   2000 requests every 10 seconds

#   Args:
#       puuid (str)
#       start (int, optional): 조회 시작 index, Defaults to 0.
#       count (int, optional): 조회할 row 수, Defaults to 20.

#   Returns:
#       [matchIds]: 전적 id 리스트
#   """
  
#   queue = 420 # rank solo
#   type = "ranked"
  
#   url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&type={type}&start={start}&count={count}"
  
#   print(f'다음으로 request : {url}')
  
#   result = requests.get(url, headers={"X-Riot-Token":API_KEY}).json()
  
#   return result


# def getMatch(matchId):
#   """
#   특정한 매치 정보 가져오기
#   2000 requests every 10 seconds
#   2023/01/21 수정 : Return type 수정 (timeline)
  
#   Args:
#       matchId (str)

#   Returns:
#       {match,teams,participants, timelines}(Nullable)
#   """
  
#   if not matchId:
#     return None
  
#   url = f"https://asia.api.riotgames.com/lol/match/v5/matches/{matchId}"
  
#   print(f'다음으로 request : {url}')
  
#   # 여기서부터는 필수 정보 제외하고 죄다 갖다 버리기
  
#   result = requests.get(url, headers={"X-Riot-Token":API_KEY}).json()
#   result_timeline = requests.get(url+'/timeline', headers={"X-Riot-Token":API_KEY}).json()
  
#   if matchId != result["metadata"]["matchId"]:
#     return None
  
#   info = result["info"]
#   info_teams = []
#   info_participants = []
  
  
#   # timeline에서 얻은 정보
#   timelines = {}
  
#   # timeline = {
#   #   "matchId" : matchId,
#   #   "puuid":puuid,
    
#   #   "itemBuild":{},
#   #   "skillBuild":[]
#   # }
  
#   match = {
#     "matchId" : matchId,
#     "gameCreation": info["gameCreation"],
#     "gameDuration": info["gameDuration"],
#     "queueId": info["queueId"]
#   }
  
#   for team in info["teams"]:
#     info_teams.append({
#       "matchId" : matchId,
#       "teamId":team["teamId"],
#       "win":team["win"],
#       "bans":team["bans"],
#       "baron":team["objectives"]["baron"]["kills"],
#       "dragon":team["objectives"]["dragon"]["kills"],
#       "tower":team["objectives"]["tower"]["kills"],
#       "totalKills":team["objectives"]["champion"]["kills"],
#     })
  
#   for participant in info["participants"]:
#     lane = participant["individualPosition"]
#     if lane == "UTILITY":
#       lane = "SUPPORT"
    
#     challenges=participant["challenges"]
    
#     info_participants.append({
#       "matchId" : matchId,
#       "teamId":participant["teamId"],
#       "puuid":participant["puuid"],
#       "totalDamageTaken":participant["totalDamageTaken"],
#       "totalDamageDealtToChampions":participant["totalDamageDealtToChampions"],
#       "wardsPlaced":participant["wardsPlaced"],
#       "wardsKilled":participant["wardsKilled"],
#       "visionWardsBoughtInGame":participant["visionWardsBoughtInGame"],
#       "summonerLevel":participant["summonerLevel"],
#       "championId":participant["championId"],
#       "championName":participant["championName"],
#       "kills":participant["kills"],
#       "deaths":participant["deaths"],
#       "lane":lane,
#       "cs":int(participant["totalMinionsKilled"])+int(participant["neutralMinionsKilled"]),
#       "killParticipation":challenges["killParticipation"],
#       "goldEarned":participant["goldEarned"],
#       "kda":str(round(float(challenges["kda"]),2)),
#       "pentaKills":participant["pentaKills"],
#       "quadraKills":participant["quadraKills"],
#       "tripleKills":participant["tripleKills"],
#       "doubleKills":participant["doubleKills"],
#       "perks":participant["perks"],
#       "item0":participant["item0"],
#       "item1":participant["item1"],
#       "item2":participant["item2"],
#       "item3":participant["item3"],
#       "item4":participant["item4"],
#       "item5":participant["item5"],
#       "item6":participant["item6"],
#     })
  
#   for initial_timeline_info in result_timeline["info"]["participants"]:
#     timelines[initial_timeline_info["participantId"]]={
#       "matchId":matchId,
#       "puuid": initial_timeline_info["puuid"],
#       "participantId":initial_timeline_info["participantId"],
#       "itemBuild":{},
#       "skillBuild":[]
#     }
    
#   frameCount=0 # frameInteval로 나눈 event frame
#   for timeline_info in result_timeline["info"]["frames"]:
#     for event in timeline_info["events"]:
      
#       # 아이템 구매 내역, 스킬 레벨업 내역이 담긴 event만 추출
#       if "type" in event and event["type"] in ["ITEM_PURCHASED","SKILL_LEVEL_UP"]:
#         event_type = event["type"]
#         participantId = event["participantId"]
#         target_timeline = timelines[participantId]
        
#         #1. 아이템 빌드 stack
#         if event_type=="ITEM_PURCHASED":
#           itemId = event["itemId"]
          
#           # 이미 interval이 존재하는 경우
#           if str(frameCount) in target_timeline["itemBuild"]:
#             target_timeline["itemBuild"][str(frameCount)].append(itemId)
#           # interval 신규 생성
#           else:
#             target_timeline["itemBuild"][str(frameCount)] = [itemId]
        
#         #2. 스킬 빌드 stack
#         elif event_type=="SKILL_LEVEL_UP":
#           target_timeline["skillBuild"].append(event["skillSlot"])
#     frameCount+=1
  
#   return { "match" :match, "teams":info_teams, "participants":info_participants, "timelines":timelines.values() }