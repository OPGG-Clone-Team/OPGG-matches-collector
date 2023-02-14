# TODO 모듈이름을 변경하던가 나중에 다른 패키지로 편입시키기

import traceback

def trycatch(cb):
  def wrapper(*args, **kwargs):
    try:
      # 2월 4일 수정 : return value 추가
      return cb(*args, **kwargs)
    except Exception as e:
      print(e)
      traceback.print_exc()
  return wrapper