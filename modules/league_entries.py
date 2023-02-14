from riot_requests import league_v4
from error.custom_exception import DataNotExists
# LEAGUEDATA db의 league_entries collection만 담당
col = "league_entries"

def updateAll(db):
  summoners = []

  summoners.extend(league_v4.get_specific_league("challengerleagues"))
  summoners.extend(league_v4.get_specific_league("grandmasterleagues"))
  summoners.extend(league_v4.get_specific_league("masterleagues"))
  
  # rank 정보 추가
  
  rank=1
  for summoner in summoners:
    summoner["rank"] = rank
    rank+=1
  
  # 추후 로깅 적용
  print('--------- 마스터 이상 소환사 정보 insert ---------')
  print(f"총 소환사 수 : {len(summoners)}")

  if(len(summoners)==0):
    print("가져온 소환사 정보가 없습니다.")
    return
  
  # db에 넣기 전 league_entires collection 비우기
  db[col].delete_many({})
  db[col].insert_many(summoners, ordered=True)

  print(f"성공적으로 {len(summoners)}명의 엔트리 정보를 업데이트했습니다.")
  return len(summoners)

def getSummonerBrief(db, summonerName):
  summoner = db[col].find_one({"summonerName":summonerName})
  
  if not summoner:
    raise DataNotExists("데이터베이스에서 소환사 정보를 찾을 수 없습니다.")
  
  return summoner

def find(db, page=1):
  limit = 100
  offset = (page - 1) * limit
  
  results = list(db[col].find(
      {}, {'_id': 0})
      .limit(limit).skip(offset))
  
  if len(results)==0:
    raise DataNotExists("데이터베이스에서 리그 엔트리 정보를 찾을 수 없습니다.")
  
  return results

if __name__=="__main__":
  updateAll()
    
