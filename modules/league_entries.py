# 상위 경로 패키지 로드
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

# 추후 환경변수 로드하는 공통로직 분리하기
from config import mongo as mongo
from riot_requests import league_v4
from trycatch_wrapper import trycatch

# LEAGUEDATA db의 league_entries collection만 담당
db = mongo.mongoClient.LEAGUEDATA
col = "league_entries"

@trycatch
def update_all():
  
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
  
  # TODO : 트랜잭션 작용하기
  # db에 넣기 전 league_entires collection 비우기
  db[col].delete_many({})
  db[col].insert_many(summoners, ordered=True)

  print(f"성공적으로 {len(summoners)}명의 엔트리 정보를 업데이트했습니다.")
    
if __name__=="__main__":
  update_all()
    
