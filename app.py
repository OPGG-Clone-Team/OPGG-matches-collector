from flask import Flask, jsonify
import os
from config.mongo import mongoClient
from modules import summoner, league_entries, match, summoner_matches
from flask_request_validator import *
from error.error_handler import error_handle
from error.custom_exception import *
from scheduler import start_schedule
from utils.date_calc import timeDifToMinute
from flask_api import status
# import logging

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

@app.route('/summoner', methods=["PATCH"], endpoint="updateSummoner")
@validate_params(
    # TODO - 정규표현식 추가하기
    Param('summonerName', JSON, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
)
def updateSummoner(valid: ValidRequest):
  """
  업데이트된 소환사 정보 보내주기
  
  Body(json):
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
  summonerName = valid.get_json()['summonerName']
  
  # 만약 갱신시각이 현재시간과 비교해서 2분 이하로 차이난다면 단순 db 조회 후 리턴
  summonerInfo = summoner.find(db, summonerName)
  if not summonerInfo:
    summonerInfo = summoner.update(db, summonerName)
  else:
    timeDiff = timeDifToMinute(summonerInfo["updatedAt"]).seconds
    if timeDiff < 60*2:
      # TODO - 나중에 다른 에러로 고치기
      raise CustomUserError(f"{timeDiff}초 전에 이미 소환사 정보를 갱신했습니다.", "Trying update too frequently", status.HTTP_400_BAD_REQUEST)
  
  result = summoner.update(db, summonerName)
  
  # 필요없는 정보 제거
  del(result["updatedAt"])
  return jsonify(result)
  

# 2월 4일 수정 : Path parameter는 공백을 받기 힘들기 때문에 Query parameter로 변경
@app.route('/match', methods=["PATCH"], endpoint = "updateSummonerMatches")
@validate_params(
    # TODO - 소환사 이름 범위 조사
    Param('summonerName', JSON, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
    Param('startIdx', JSON, int, default=0, required=False, rules=[ValidateStartIdxParam()]),
    Param('size', JSON, int, default=30, required=False, rules=[ValidateStartIdxParam()]),
)
def updateSummonerMatches(valid: ValidRequest):
  """
  업데이트된 최근 소환사의 전적 가져오기

  Body(json):
      summonerName(String, required)
      startIdx(Integer, Default to 0) : 검색 시작 인덱스
      size(Integer, Default to 30) : 검색할 인덱스 수

  Returns:
      {
        "summoner"=summonerInfo,
        "matches"=matches(List, [{
          match,
          teams,
          participants
        }]) : 소환사의 최근 전적정보 리스트
      }
  """
  # 소환사 이름을 받고, 이 소환사의 summoner_matches를 갱신
  # parameter로 startIdx, size를 받고, 이 수만큼 db에서 매치정보 가져오기
  # 각각의 matchId에 대해 전적정보 갱신
  parameters = valid.get_json()
  summonerName = parameters["summonerName"]
  startIdx = parameters["startIdx"]
  size = parameters["size"]
  
  summonerInfo = summoner.find(db, summonerName)
  if not summonerInfo:
    summonerInfo = summoner.update(db, summonerName)
  else:
    # 만약 갱신시각이 현재시간과 비교해서 2분 이하로 차이난다면 단순 db 조회 후 리턴
    timeDiff = timeDifToMinute(summonerInfo["updatedAt"]).seconds
    if timeDiff < 60*2:
      # TODO - 나중에 다른 에러로 고치기
      raise CustomUserError(f"{timeDiff}초 전에 이미 소환사 정보를 갱신했습니다.", "Trying update too frequently", status.HTTP_400_BAD_REQUEST)
  
  # FIXME - 트랜잭션 임시 비활성화    
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  puuid = summoner_matches.update(db, summonerName)
  
  # 최근 소환사의 matchId 가져오기
  matchIds = summoner_matches.findRecentMatchIds(db, puuid, startIdx, size)
  
  result = match.findOrUpdateAll(db, matchIds)

  return jsonify({
    "summoner": summonerInfo,
    "matches":result
    })


@app.route('/summoner', methods=["GET"], endpoint="getSummonerAndMatches")
@validate_params(
    # TODO - 정규표현식 추가하기
    Param('summonerName', GET, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
    Param('startIdx', GET, int, default=0, required=False, rules=[ValidateStartIdxParam()]),
    Param('size', GET, int, default=30, required=False, rules=[ValidateStartIdxParam()]),
)
def getSummonerAndMatches(valid: ValidRequest):
  """소환사 이름 받아서 "갱신되지 않은" 소환사 정보 + 소환사 전적정보를 리턴
  
  Query Parameter:
      summonerName(String, required)
      startIdx(Integer, Default to 0) : 검색 시작 인덱스
      size(Integer, Default to 30) : 검색할 인덱스 수

  Returns:
      _type_: _description_
  """
  # 
  parameters = valid.get_params()
  summonerName = parameters["summonerName"]
  startIdx = parameters["startIdx"]
  size = parameters["size"]
  
  summonerInfo = summoner.find(db, summonerName)
  matchIds = summoner_matches.findRecentMatchIds(db, summonerInfo["puuid"], startIdx, size)
  matches = match.findOrUpdateAll(db, matchIds)
  
  return jsonify({
    "summoner": summonerInfo,
    "matches":matches
    })

# TODO - 현재 Riot Api에서 league_entries 소환사이름정보와 summoner 소환사이름정보가 불일치하는 현상 발생
# 추후 API 재발급 시 고려해봐야 할듯
@app.route('/league-entry', methods=["GET"], endpoint="getLeagueEntries")
@validate_params(
    Param('page', GET, int, default=1, required=False, rules=[ValidateStartIdxParam()]),
)
def getLeagueEntries(valid:ValidRequest):
  parameters = valid.get_params()
  page = parameters["page"]
  
  result = league_entries.find(db, page)
  
  return jsonify(result)


@app.route('/batch', methods=["POST"])
def leagueEntriesBatch(): # 배치 수행
  """수동 배치돌리기
  league_entries 업데이트해주기
  2023/02/14 수정 : 사용자가 접근할 수 있는 배치로 따로 빼기
  
  Returns:
      updated(int) : 마스터 이상 유저 업데이트수
  """
  # TODO Riot API Upgrade 후 league_entries에 있는 모든 소환사 및 소환사 전적정보 갱신
  
  # FIXME - 트랜잭션 임시 비활성화 (트랜잭션을 중간과정에 삽입해야 할듯)
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  updated_summoner_count=league_entries.updateAll(db)
  return {"status":"ok","updated":updated_summoner_count}

@app.route('/batch/summoner', methods=["POST"])
def summonerBatch(): # 배치 수행
  """수동 배치돌리기
  league_entries 내에 있는 소환사 정보 모두 업데이트해주기
  실행 당시의 league_entries 안에 있는 소환사들만 업데이트해주기
  
  Returns:
      updated(int) : 마스터 이상 유저 업데이트수
  """
  # TODO Riot API Upgrade 후 league_entries에 있는 모든 소환사 및 소환사 전적정보 갱신
  
  # FIXME - 트랜잭션 임시 비활성화 (트랜잭션을 중간과정에 삽입해야 할듯)
  # with mongoClient(app).start_session() as session:
  #   with session.start_transaction():
  updated_summoner_count=summoner.updateAll(db)
  return {"status":"ok","updated":updated_summoner_count}

# 스케줄링 걸기
start_schedule([
  {
    "method":leagueEntriesBatch, 
    "time":2
  },
  {
    "method":summonerBatch,
    # TODO - 우선 소환사 정보갱신은 12시간 단위로 실행하도록 설정
    "time":60*12
  },
  ])


def create_app():
  return app

if __name__ == "__main__":
  app.run(
    host = app.config["FLASK_HOST"], 
    port=app.config["FLASK_PORT"])
  