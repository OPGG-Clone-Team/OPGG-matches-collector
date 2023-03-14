import re
import logging

logger = logging.getLogger("app")

def makeInternalName(str):
  # str을 전부 소문자로 변환 후 공백 모두 제거해서 리턴
  return str.lower().replace(" ", "")

def isValidInternalName(str):
  # auto complete 수행하기 전 검색할 수 있는 단어인지 판별
  # 조건 : 안에 영문자, 한글, 숫자, 공백만 들어갈 수 있음
  # True 반환 시 올바른 
  str = makeInternalName(str)
  
  if len(str)==0:
    return False
  
  p = re.compile("[^a-z0-9가-힣]")
  
  result = p.search(str)
  
  if result==None:
    return True
  
  # logger.info("형식에 맞지 않는 문자 발견")
  return False