import os
from error import custom_exception
from flask_api import status
from riot_requests.common import delayableRequest

def get_specific_league(league, queue="RANKED_SOLO_5x5"):
  """
  해당 league에 존재하는 모든 소환사 정보 가져오기\n
  50 requests every 10 seconds

  Args:
      league (str): should be in ["challengerleagues", "grandmasterleagues","masterleagues"].
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

  ## delayable
  result = delayableRequest(url, 20)
  entries = result["entries"]
  
  if not entries or not isinstance(entries, list):
    raise custom_exception.CustomUserError(
      "리그 엔트리 정보를 가져오는 데 실패했습니다.", 
      "Result of request to Riot not exists", status.HTTP_404_NOT_FOUND )

  # TODO - 요구사항 확장 시 이부분은 고쳐야함
  entries.sort(key = lambda x : x["leaguePoints"], reverse=True)
  
  # 티어, 큐 업데이트
  for entry in entries:
    entry["queue"] = league[:-7]
    entry["tier"] = entry["rank"]
  
  return entries

