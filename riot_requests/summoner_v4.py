import requests
import os

def getSummoner(summonerId):
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
  
  url = f"https://kr.api.riotgames.com/lol/summoner/v4/summoners/{summonerId}"

  # 추후 logging 적용
  print(f'다음으로 request : {url}')
  result = requests.get(url, headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}, timeout = 10).json()
  
  #TODO 예외처리 깔끔하게 하기
  if "id" not in result and "status" in result:
    return None
  
  return result