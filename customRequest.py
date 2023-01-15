import requests
import os

API_KEY = os.getenv("RIOT_API_KEY_1")


def league_v4(tier, queue="RANKED_SOLO_5x5"):
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
  
  summoners=[]
  
  url = f"https://kr.api.riotgames.com/lol/league/v4/{tier}/by-queue/{queue}"

  # 추후 logging 적용
  print(f'다음으로 request : {url}')

  result = requests.get(url, headers={"X-Riot-Token":API_KEY}).json() ## list type expected
  
  entries = result["entries"]
  
  if not entries: # fetching한 데이터가 비어 있으면 함수 즉시 종료
    return summoners
  
  # 만약 list데이터로 넘어오지 않는다면 (ERROR 발생) response 출력 후 함수 종료
  if not isinstance(entries, list): 
    print(result)
    return summoners
  
  summoners.extend(entries)
  return summoners

def getSummoner(id):
  """
  summonerId로 Summoner 정보 가져오기\n
  1600 requests every 1 minutes\n
  경고 - Consistently looking up summoner ids that don't exist will result in a blacklist.\n
  
  Args:
      id (str): summonerId

  Returns:
      Summoner: {
        "id": 소환사 ID,
        "accountId": 소환사 계정 ID,
        "puuid": 소환사 PUUID,
        "name": 소환사명,
        "profileIconId": 프로필 아이콘 id,
        "revisionDate": 소환사 정보 최종 수정일,
        "summonerLevel": 소환사 레벨,
        "queryAllowTime": 해당 소환사를 query 가능한 시간, default : null
      }
  """
  
  url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{id}"

  # 추후 logging 적용
  print(f'다음으로 request : {url}')
  result = requests.get(url, headers={"X-Riot-Token":API_KEY}).json()
  
  if "id" not in result:
    return {}
  
  return result