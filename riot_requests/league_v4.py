import os
from error import custom_exception
from flask_api import status
from common import delayeableRequest

def get_specific_league(league, queue="RANKED_SOLO_5x5"):
  """
  해당 league에 존재하는 모든 소환사 정보 가져오기\n
  50 requests every 10 seconds

  Args:
      league (str, required): should be in ["challengerleagues", "grandmasterleagues","masterleagues"].
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
  if league not in ["challengerleagues", "grandmasterleagues","masterleagues"]:
    return []
  
  url = f"https://kr.api.riotgames.com/lol/league/v4/{league}/by-queue/{queue}"
  headers={"X-Riot-Token":os.getenv("RIOT_API_KEY_1")}
  # 추후 logging 적용
  print(f'다음으로 request : {url}')

  ## delayable
  result = delayeableRequest(url, headers, 10)
  entries = result["entries"]
  
  if not entries or not isinstance(entries, list):
    raise custom_exception.CustomUserError(
      "리그 엔트리 정보를 가져오는 데 실패했습니다.", 
      "Result of request to Riot not exists", status.HTTP_404_NOT_FOUND )

  entries.sort(key = lambda x : x["leaguePoints"], reverse=True)
  # 티어, 큐, 순위 업데이트
  for entry in entries:
    entry["queue"] = league[:-7]
    entry["tier"] = entry["rank"]
  
  return entries

