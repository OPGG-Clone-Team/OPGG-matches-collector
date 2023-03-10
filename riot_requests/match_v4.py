
from error import custom_exception
from flask_api import status
from riot_requests.common import delayableRequest
import logging

logger = logging.getLogger("app")

def getSummonerMatches(puuid, start=0, count = 30):
  """
  유저의 최근 전적 id 리스트 가져오기
  2000 requests every 10 seconds

  2023.02.06 추가 : killParticipations가 들어오지 않는 데이터 확인, 에러 처리
  2023.02.06 추가 : participants의 assists 필드 추가
  2023.03.06 추가 : participants의 win, gameDuration 필드 추가

  Args:
      puuid (str)
      start (int, optional): 조회 시작 index, Defaults to 0.
      count (int, optional): 조회할 row 수, Defaults to 30.

  Returns:
      [matchIds]: 전적 id 리스트
  """
  
  queue = 420 # rank solo
  type = "ranked"
  
  url = f"https://asia.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?queue={queue}&type={type}&start={start}&count={count}"
  
  result = delayableRequest(url, 30)
  
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
  
  # 여기서부터는 필수 정보 제외하고 죄다 갖다 버리기
  result = delayableRequest(url, 20)
  result_timeline = delayableRequest(url+'/timeline', 20)
  
  # 코드 수정 : result와 result_timeline 둘 중 하나도 존재하지 않으면 return none
  if result.get("status") or result_timeline.get("status"):
    raise custom_exception.CustomUserError(
      "매치정보를 가져오는 데 실패했습니다.", 
      "Result of request to Riot not exists", status.HTTP_404_NOT_FOUND )
  
  info = result["info"]
  info_teams = []
  info_participants = []
  
  # timeline에서 얻은 정보
  timelines = {}
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
  
  if info_teams[0]["win"]=="true":
    win_team_id=info_teams[0]["teamId"]
  else:
    win_team_id=info_teams[1]["teamId"]
  
  for participant in info["participants"]:
    lane = participant["teamPosition"]
    # if lane == "UTILITY":
    #   lane = "SUPPORT"
    
    if lane not in ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]:
      logger.warning(f"잘못된 라인 정보가 들어왔습니다. {lane}")
    else:
      if lane == "UTILITY":
        lane=="SUPPORT"
    
    challenges=participant["challenges"]
    
    # 킬관여율 필드 추가
    # info["teams"]에서 teamId가 일치하는거 찾고 거기서 totalKill 가져오기
    # challenges에 killParticipations 필드가 존재하지 않는다면 직접 계산 후 소수 2번째 자리까지 반올림
    teamId = participant["teamId"]
    total_team_kills = int(list(filter(lambda x: x["teamId"]==teamId, info_teams))[0]["totalKills"])
    killParticipation = challenges.get("killParticipation")
    if not killParticipation:
      if total_team_kills==0:
        killParticipation = 0
      else:
        killParticipation = round(((participant["kills"]+participant["assists"])/ total_team_kills), 2)
    
    # 승리 여부
    if win_team_id == participant["teamId"]:
      win="true"
    else:
      win="false"
    
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
      "assists": participant["assists"],
      "lane":lane,
      "cs":int(participant["totalMinionsKilled"])+int(participant["neutralMinionsKilled"]),
      # 로직 수정
      "killParticipation":killParticipation,
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
      # 필드 두개 추가
      "win":win,
      "gameDuration": info["gameDuration"],
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
  
  # 2월 6일 수정 : dict_values로 리턴되어 list로 반환하지 않는 이슈 수정
  return { 
          "match" :match, 
          "teams":info_teams, 
          "participants":info_participants, 
          "timelines":list(timelines.values()) }