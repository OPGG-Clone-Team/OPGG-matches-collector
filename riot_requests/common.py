import requests, time
from flask_api import status
import logging

logger = logging.getLogger("app")

# TODO - 최종 시간 제한도 걸어놔야 api 서버 상황에 대처할 수 있을 듯
def delayableRequest(url, headers, timeout):
  """Riot API Rate Limit에 의해 지연될 수 있는 요청 Handle

  Args:
      url (str): 요청 url
      headers : RIOT API KEY 정보를 담고 있는 헤더
      timeout (int): 지연시킬 시간(seconds)

  Returns:
      request (any)
  """
  
  logger.info(f'다음으로 request : {url}')  
  request = requests.get(url, headers=headers, timeout=timeout)
  
  # API Rate Limit을 초과하지 않을 때까지 계속 반복, timeout만큼 polling
  while request.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
    logger.info("다시 호출")
    logger.info(request.json())
    
    time.sleep(timeout)
    request = requests.get(url, headers=headers, timeout=timeout)
  
  return request.json()