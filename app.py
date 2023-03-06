from flask import Flask, jsonify, request
import os
from config.mongo import mongoClient # 데이터베이스 연동

app=Flask(__name__)

log_dir = './logs' # 로그 남길 디렉토리 (없으면 자동으로 생성)
if not os.path.exists(log_dir):
    os.mkdir(log_dir)
    
import utils.initialize_logger # 로거 최초 동작
import logging
from flask_request_validator import * # parameter validate
from error.error_handler import error_handle # flask에 에러핸들러 등록
from error.custom_exception import * # custom 예외
from config.config import config # 최초 환경변수 파일 로드
from scheduler import start_schedule # 스케줄러 로드
from modules import summoner, league_entries, match, summoner_matches
from modules.analysis import champion
from riot_requests import spectator_v4
from bson import json_util
import json

logger = logging.getLogger("app") # 로거

config_type = os.getenv("APP_ENV") if os.getenv("APP_ENV") else "default"
app.config.from_object(config[config_type]) # 기본 앱 환경 가져오기

error_handle(app) # app 공통 에러 핸들러 추가

db = mongoClient(app).LEAGUEDATA # pymongo connection

# Param의 request_parameter_type
# GET : 쿼리 파라미터
# FORM : 폼 형태로 들어온 값
# JSON : body로 들어온 값
# PATH : Path 파라미터

# TODO - summonerName trim()처리
@app.route('/summoner', methods=["PATCH"], endpoint="updateSummoner")
@validate_params(
    # TODO - 정규표현식 추가하기
    Param('summonerName', JSON, str, required=True, rules=CompositeRule(MinLength(2), MaxLength(40))),
)
def updateSummoner(valid: ValidRequest):
  """
  소환사 정보 업데이트 후 보내주기
  
  RequestBody(json):
      summonerName(str) : 소환사이름 
  
  Returns:
      {
        name(String) : 소환사 이름
        profileIconId(Integer) : 소환사 프로필 아이콘 ID
        puuid(Integer) : 소환사 puuid
        revisionDate(Integer, epoch milliseconds) : 소환사 정보 최종 수정일
        summonerLevel(Integer) : 소환사 레벨
      }
  """
  summonerName = valid.get_json()['summonerName']
  
  result = summoner.updateBySummonerName(db, summonerName)
  
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
      summonerName (str)
      startIdx (int, Default to 0) : 검색 시작 인덱스
      size (int, Default to 30) : 검색할 인덱스 수

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
  
  # 2023/02/24 수정 : 무조건 소환사 정보 같이 업데이트 해주는게 나을 듯
  summonerInfo = summoner.updateBySummonerName(db, summonerName)
  
  puuid = summoner_matches.update(db, summonerName = summonerName)
  
  # 최근 소환사의 matchId 가져오기
  matchIds = summoner_matches.findRecentMatchIds(db, puuid, startIdx, size)
  
  result = match.findOrUpdateAll(db, matchIds)
  ingame = spectator_v4.requestIngameInfo(summonerInfo["id"])
  
  
  return jsonify({
    "summoner": summonerInfo,
    "matches":result,
    "ingame":ingame
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
  
  summonerInfo = summoner.findBySummonerName(db, summonerName)
  if not summonerInfo:
    raise DataNotExists("DB에 소환사 정보가 없습니다.")
  
  matchIds = summoner_matches.findRecentMatchIds(db, summonerInfo["puuid"], startIdx, size)
  matches = match.findOrUpdateAll(db, matchIds)
  ingame = spectator_v4.requestIngameInfo(summonerInfo["id"])
  
  return jsonify({
    "summoner": summonerInfo,
    "matches":matches,
    "ingame":ingame
    })

@app.route('/league-entry', methods=["GET"], endpoint="getLeagueEntries")
@validate_params(
    Param('page', GET, int, default=1, required=False, rules=[ValidateStartIdxParam()]),
)
def getRank(valid:ValidRequest):
  parameters = valid.get_params()
  page = parameters["page"]
  
  result = league_entries.find(db, page)
  
  return jsonify(result)


@app.route('/batch', methods=["POST"])
def leagueEntriesBatch():
  """수동 배치돌리기
  league_entries 가져와서 rank정보 업데이트해주기
  2023/02/14 수정 : 사용자가 접근할 수 있는 배치로 따로 빼기
  
  Returns:
      updated(int) : 마스터 이상 유저 업데이트수
  """

  logger.info("랭킹정보 갱신 시작")
  updated_summoner_count=league_entries.updateAll(db)
  return {"status":"ok","updated":updated_summoner_count}


# TODO - 추후 개발
@app.route('/batch/match', methods=["POST"])
def matchBatch(): # 전적정보 배치 수행
  """수동 배치돌리기
  소환사 정보 내에 있는 모든 소환사들의 summoner_match와 match정보를 업데이트
  실행 당시의 league_entries 안에 있는 소환사들만 업데이트해주기
  
  Returns:
      updated(int) : 마스터 이상 유저 업데이트수
  """
  # TODO Riot API Upgrade 후 league_entries에 있는 모든 소환사 및 소환사 전적정보 갱신
  
  # 1. league_entries 가져오기
  summonerIds = league_entries.findAllSummonerId(db)
  # 2. league_entries 안의 소환사 아이디를 돌아가면서 summoner_matches를 업데이트하기
  for summonerId in [d['summonerId'] for d in summonerIds if 'summonerId' in d]:
    try:
      puuid = summoner_matches.update(db, summonerId = summonerId)
      match_ids = summoner_matches.findRecentMatchIds(db, puuid)
      
      for match_id in match_ids:
        match.findOrUpdate(db, match_id)
      
    except DataNotExists as e:
      logger.warning("DB에 해당 소환사 정보가 존재하지 않아 다음 소환사로 넘어감")
    
  return {"status":"ok","message":"전적 정보 배치가 완료되었습니다."}

@app.route('/test', methods=["POST"])
def test():
  
  
  return champion.championAnalysis(db)
  # return json.loads(json_util.dumps(result))

# 스케줄링 걸기
# TODO - matchBatch to cron (새벽 4시~ 이후 몇시간동안 안돌아가도록)
start_schedule([
  # {
  #   "job":leagueEntriesBatch,
  #   "method":"interval", 
  #   "time":2
  # },
  
  # 4시 정각에 돌아가도록 설정
  {
    "job":matchBatch,
    "method":"cron",
    "time":{
      "hour":app.config["BATCH_HOUR"]
    }
  }
  ])

if __name__ == "__main__":
  app.run(
    host = app.config["FLASK_HOST"], 
    port=app.config["FLASK_PORT"])
  