import redis, json, logging

logger = logging.getLogger("app")

# redis-cli에서 꺼낼 떄 lrange my-queue 0 30 으로 사용
class RedisQueue(object):
  def __init__(self, max_size = 30, **redis_kwargs):
    # """
    #   name(key), host, port, db정보 넘겨주기
    # """
    self.rq = redis.Redis(**redis_kwargs)
    self.max_size = max_size
    
  def size(self, key):  # 큐 크기 확인
    return self.rq.llen(key)
  
  def isEmpty(self, key):  # 비어있는 큐인지 확인
    return self.size(key) == 0

  def put(self, key, value):  # 데이터 넣기
    
    self.rq.lpush(key, json.dumps(value))  # left push
    self.rq.ltrim(key, 0, self.max_size-1) # 최대크기를 초과한 경우 자르기

  def putAll(self, key, values):
    for value in values:
      self.put(key, value)
  
  def get_without_pop(self, key):  # 꺼낼 데이터 조회
    if self.isEmpty(key):
        return None
    
    return json.loads(self.rq.lindex(key, self.size(key)-1))
    
  
def redisClient(app):
  return RedisQueue(
    host = app.config.get("REDIS_HOST") or "localhost", 
    port = int(app.config.get("REDIS_PORT")) or 6379, 
    db = 0)


