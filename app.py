from flask import Flask, jsonify
import os
from config.mongo import mongoClient
from modules import summoner, league_entries, match, summoner_matches
from flask_request_validator import *
from error.error_handler import error_handle
from error.custom_exception import *

# 최초 환경변수 파일 로드
from config.config import config

app=Flask(__name__)

# 1. 기본 앱 환경 가져오기
config_type = os.getenv("FLASK_ENV") if os.getenv("FLASK_ENV") else "default"
app.config.from_object(config[config_type])

# app 공통 에러 핸들러 추가
error_handle(app)

# MONGO DB
db = mongoClient(app).LEAGUEDATA

# Param의 request_parameter_type
# GET : 쿼리 파라미터
# FORM : 폼 형태로 들어온 값
# JSON : body로 들어온 값
# PATH : Path 파라미터
@app.route('/summoner', methods=["GET"], endpoint="updateSummoner")
@validate_params(
    # TODO - 정규표현식 추가하기
    Param('summonerName', GET, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
)
def updateSummoner(valid: ValidRequest):
  """
  업데이트된 소환사 정보 보내주기
  
  Query Params:
      summonerName(str)
  
  Returns:
      {
        name(String) : 소환사 이름
        profileIconId(Integer) : 소환사 프로필 아이콘 ID (with CDN)
        puuid(Integer) : 소환사 puuid
        revisionDate(Integer, epoch milliseconds) : 소환사 정보 최종 수정일
        summonerLevel(Integer) : 소환사 레벨
      }
  """
  summonerName = valid.get_params()['summonerName']
  
  # FIXME - 트랜잭션 임시 비활성화
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  result = summoner.update(db, summonerName)
  return jsonify(result)

# 2월 4일 수정 : Path parameter는 공백을 받기 힘들기 때문에 Query parameter로 변경
@app.route('/match', methods=["GET"], endpoint = "updateSummonerMatches")
@validate_params(
    # TODO - 소환사 이름 범위 조사
    Param('summonerName', GET, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
    Param('startIdx', GET, int, default=0, required=False, rules=[ValidateStartIdxParam()]),
    Param('size', GET, int, default=30, required=False, rules=[ValidateStartIdxParam()]),
)
def updateSummonerMatches(valid: ValidRequest):
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
  # 각각의 matchId에 대해 전적정보 갱신
  parameters = valid.get_params()
  summonerName = parameters["summonerName"]
  startIdx = parameters["startIdx"]
  size = parameters["size"]
  
  result = []
  
  # FIXME - 트랜잭션 임시 비활성화    
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  puuid = summoner_matches.update(db, summonerName)
  
  # 최근 소환사의 matchId 가져오기
  matchIds = summoner_matches.findRecentMatchIds(db, puuid, startIdx, size)
  
  for matchId in matchIds:
    result.append(match.update(db, matchId))

  return jsonify(result)

@app.route('/batch', methods=["POST"])
def runBatch(): # 배치 수행
  # TODO Riot API Upgrade 후 league_entries에 있는 모든 소환사 및 소환사 전적정보 갱신
  
  # FIXME - 트랜잭션 임시 비활성화 (트랜잭션을 중간과정에 삽입해야 할듯)
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  updated_summoner_count=league_entries.update_all(db)
  return {"status":"ok","updated":updated_summoner_count}



def create_app():
  return app


if __name__ == "__main__":
  app.run(host = app.config["FLASK_HOST"] , port=app.config["FLASK_PORT"])
  