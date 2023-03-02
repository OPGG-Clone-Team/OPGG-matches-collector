from error.custom_exception import *
from riot_requests.common import delayableRequest
import logging
from flask_api import status

logger = logging.getLogger("app")

def requestIngameInfo(summonerId):
  
  url = f"https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summonerId}"
  # request 
  request = delayableRequest(url, 20)
  
  # ingame info validate 기준
  # 1. 소환사 정보를 찾는 데 성공했지만 현재 게임 중이 아닌 경우
  # {
  #   "status": {
  #       "message": "Data not found",
  #       "status_code": 404
  #   }
  # }
  # 2. 소환사 정보를 찾지 못한 경우
  # {
  #     "status": {
  #         "message": "Bad Request - Exception decrypting qUgrnCloy0fSUZj9cLvLI3wOJOdz1sUv8Uo8hXOhMsMYRkg",
  #         "status_code": 400
  #     }
  # }  
  
  if(request["status"]["status_code"] in [status.HTTP_400_BAD_REQUEST,status.HTTP_404_NOT_FOUND]):
    logger.info("소환사 인게임 정보가 존재하지 않거나 소환사 정보가 존재하지 않습니다.")
    return {}
  
  # 3. 현재 인게임중인 소환사 정보인 경우
  #   {
  #     "gameId": 6387873544,
  #     "mapId": 11,
  #     "gameMode": "CLASSIC",
  #     "gameType": "MATCHED_GAME",
  #     "gameQueueConfigId": 420,
  #     "participants": [
  #         {
  #             "teamId": 100,
  #             "spell1Id": 14,
  #             "spell2Id": 4,
  #             "championId": 412,
  #             "profileIconId": 22,
  #             "summonerName": "qweasdreczc",
  #             "bot": false,
  #             "summonerId": "UF3_Cvfm8FwQ97rXkc_21r-KFkrB4ydA0ks4qYNUWi9jC8mVFMusG1FCIA",
  #             "gameCustomizationObjects": [],
  #             "perks": {
  #                 "perkIds": [
  #                     8351,
  #                     8313,
  #                     8316,
  #                     8347,
  #                     8473,
  #                     8242,
  #                     5005,
  #                     5003,
  #                     5002
  #                 ],
  #                 "perkStyle": 8300,
  #                 "perkSubStyle": 8400
  #             }
  #         }],
  #     "observers": {
  #         "encryptionKey": "oOXuJLFtG2+QBByz+QdvCZI/iL88c/GV"
  #     },
  #     "platformId": "KR",
  #     "bannedChampions": [
  #         {
                # -1 : 밴 안했음
  #             "championId": 51, 
  #             "teamId": 100,
  #             "pickTurn": 1
  #         },
  #     ],
  #     "gameStartTime": 1677735200756,
  #     "gameLength": 861
  # }
  
  del request["observers"]
  
  return request