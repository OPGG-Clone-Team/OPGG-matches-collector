import requests, time
from flask_api import status

def delayeableRequest(url, headers, timeout):
  request = requests.get(url, headers=headers, timeout=timeout)
  
  # API Rate Limit을 초과하지 않을 때까지 계속 반복
  while request.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
    # thread blocking이기 때문에 상관없음
    print(request.json())
    time.sleep(10)
    request = requests.get(url, headers=headers, timeout=timeout)
    
    # raise RateLimiteExceededError("라이엇 API 요청 수가 제한을 초과했습니다.")
  
  return request.json()