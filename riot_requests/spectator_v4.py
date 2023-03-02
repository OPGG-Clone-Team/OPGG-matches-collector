from error.custom_exception import *
from riot_requests.common import delayableRequest
import logging

logger = logging.getLogger("app")

def requestIngameInfo(summonerId):
  
  url = f"https://kr.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summonerId}"
  # request 
  request = delayableRequest(url, 20)
  logger.info(request)
  
  return request