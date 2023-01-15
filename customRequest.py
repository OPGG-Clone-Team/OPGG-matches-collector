import requests
import os

API_KEY = os.getenv("RIOT_API_KEY_1")
# iter = 반복 횟수

# tier에 존재하는 모든 소환사 정보 가져오기
# 마그마챌 유저들만 request
def league_exp_v4(tier, summoners, queue="RANKED_SOLO_5x5", division="I"):
  
  if tier not in ["CHALLENGER", "GRANDMASTER","MASTER"]:
    return None
  
  for i in range(1, iter+1):
    url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={i}"

    # 추후 logging 적용
    print(f'다음으로 request : {url}')

    results = requests.get(url, headers={"X-Riot-Token":API_KEY}).json() ## list type expected
    
    if not results: # fetching한 데이터가 비어 있으면 함수 즉시 종료
      return summoners
    
    # 만약 list데이터로 넘어오지 않는다면 (ERROR 발생) response 출력 후 함수 종료
    if not isinstance(results, list): 
      print(results)
      return summoners
    
    summoners.extend(results)

  return summoners

def league_exp_v4(tier, summoners, queue="RANKED_SOLO_5x5", division="I"):
  
  if tier not in ["CHALLENGER", "GRANDMASTER","MASTER"]:
    return None
  
  for i in range(1, iter+1):
    url = f"https://kr.api.riotgames.com/lol/league-exp/v4/entries/{queue}/{tier}/{division}?page={i}"

    # 추후 logging 적용
    print(f'다음으로 request : {url}')

    results = requests.get(url, headers={"X-Riot-Token":API_KEY}).json() ## list type expected
    
    if not results: # fetching한 데이터가 비어 있으면 함수 즉시 종료
      return summoners
    
    # 만약 list데이터로 넘어오지 않는다면 (ERROR 발생) response 출력 후 함수 종료
    if not isinstance(results, list): 
      print(results)
      return summoners
    
    summoners.extend(results)

  return summoners