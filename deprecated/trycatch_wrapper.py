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
