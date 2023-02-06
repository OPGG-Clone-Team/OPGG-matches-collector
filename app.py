from flask import Flask, request, jsonify
from flask_api import status
import os
from config.mongo import mongoClient
from modules import summoner, league_entries, match, summoner_matches

# 최초 환경변수 파일 로드
from config.config import config

app=Flask(__name__)

# 1. 기본 앱 환경 가져오기
config_type = os.getenv("FLASK_ENV") if os.getenv("FLASK_ENV") else "default"
app.config.from_object(config[config_type])

# MONGO DB
db = mongoClient(app).LEAGUEDATA

@app.route('/summoner', methods=["GET"])
def updateSummoner():
  """
  업데이트된 소환사 정보 보내주기
  
  Query Params:
      summonerName(String)
  
  Returns:
      {
        name(String) : 소환사 이름
        profileIconId(Integer) : 소환사 프로필 아이콘 ID (with CDN)
        puuid(Integer) : 소환사 puuid
        revisionDate(Integer, epoch milliseconds) : 소환사 정보 최종 수정일
        summonerLevel(Integer) : 소환사 레벨
      }
  """
  
  summonerName = request.args.get("summonerName")
  
  with mongoClient(app).start_session() as session:
    with session.start_transaction():
      result = summoner.update(db, summonerName)
  return jsonify(result)

# 2월 4일 수정 : Path parameter는 공백을 받기 힘들기 때문에 Query parameter로 변경
@app.route('/match', methods=["GET"])
def updateSummonerMatches():
  """
  업데이트된 최근 소환사의 전적 가져오기

  Query Parameter:
      summonerName(String, required)
      startIdx(Integer, Default to 0) : 검색 시작 인덱스
      size(Integer, Default to 30) : 검색할 인덱스 수

  Returns:
      matches(List, [{
        match,
        teams,
        participants
      }]) : 소환사의 최근 전적정보 리스트
  """
  # 소환사 이름을 받고, 이 소환사의 summoner_matches를 갱신
  # parameter로 startIdx, size를 받고, 이 수만큼 db에서 매치정보 가져오기
  summonerName = request.args.get("summonerName")
  
  # TODO startIdx 없을 때 예외처리
  # TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
  startIdx = int(request.args.get("startIdx")) or 0
  size = int(request.args.get("size")) or 30
  
  # TODO 추후 공통 에러핸들러 추가
  if not summonerName:
    return {"message":"소환사 이름을 입력해주세요."}, status.HTTP_404_NOT_FOUND
  
  # 각각의 matchId에 대해 전적정보 갱신
  result = []
      
  with mongoClient(app).start_session() as session:
    with session.start_transaction():
      puuid = summoner_matches.update(db, summonerName)
      
      # 최근 소환사의 matchId 가져오기
      matchIds = summoner_matches.findRecentMatchIds(db, puuid, startIdx, size)
      
      for matchId in matchIds:
        result.append(match.update(db, matchId))

  return jsonify(result)

@app.route('/batch', methods=["POST"])
def runBatch(): # 배치 수행
  # TODO Riot API Upgrade 후 league_entries에 있는 모든 소환사 및 소환사 전적정보 갱신
  with mongoClient(app).start_session() as session:
    with session.start_transaction():
      updated_summoner_count=league_entries.update_all(db)
      return {"status":"ok","updated":updated_summoner_count}

def create_app():
  return app

# def mongoDB():
#   conn = mongoClient(app)
#   return conn[app.config["MONGO_DATABASE"]]

if __name__ == "__main__":
  app.run(host = app.config["FLASK_HOST"] , port=app.config["FLASK_PORT"])
  