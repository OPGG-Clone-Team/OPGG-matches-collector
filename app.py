from flask import Flask, request, jsonify
from flask_api import status
import json, os

# 최초 환경변수 파일 로드
with open('config/config.json') as f:
  config = json.load(f)

def create_app():
  app=Flask(__name__)
  # flask app config
  # 1. 기본 앱 환경 가져오기
  APP_ENV = os.environ.get("APP_ENV")
  
  # 2. 기본 앱 환경에 따라서 config 파일을 다르게 가져오기
  app.config.update(
    PORT = config[APP_ENV]["FLASK_PORT"],
    MONGO_URI = config[APP_ENV]["MONGO_URI"],
  )
  
  from modules import summoner, league_entries, match, summoner_matches
  
  # 3. DEFAULT 환경 로드
  app.config.update(
    API_KEY = config["DEFAULT"]["RIOT_API_KEY_1"]
  )
  
  @app.route('/summoner', methods=["GET"])
  def updateSummoner(): # 소환사 정보 갱신
    summonerName = request.args.get("summonerName")
    result = summoner.findSummoner(app, summonerName)
    return jsonify(result)
  
  # 2월 4일 수정 : Path parameter는 공백을 받기 힘들기 때문에 Query parameter로 변경
  @app.route('/match', methods=["GET"])
  def updateSummonerMatches():
    # 소환사 이름을 받고, 이 소환사의 summoner_matches를 갱신
    summonerName = request.args.get("summonerName")
    
    # TODO 추후 공통 에러핸들러 추가
    if not summonerName:
      return {"message":"소환사 이름을 입력해주세요."}, status.HTTP_404_NOT_FOUND
    
    # parameter로 startIdx, size를 받고, 이 수만큼 db에서 매치정보 가져오기
    startIdx = request.args.get("startIdx") or 0
    size = request.args.get("size") or 30
    
    # 1. matchIds(list) = summoner_matches.update()
    
    # print(matchIds)
    # 2. 각각의 matchId에 대해 match.update()
    # result = []
    # for matchId in matchIds:
    #   result.append(match.update(app, matchId))
      
    # 3. 모든 결과값을 저장해서 리턴
    return "ok"
  
  
  @app.route('/batch', methods=["POST"])
  def runBatch(): # 배치 수행
    # 임시로 league_entries update
    league_entries.update_all(app)
    return {"status":"ok"}
  
  return app

app=create_app()
if __name__ == "__main__":
  # app = create_app()
  app.run(host = "0.0.0.0" , port=app.config["PORT"], debug=True)
  