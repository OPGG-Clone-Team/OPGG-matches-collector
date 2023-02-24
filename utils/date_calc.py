import datetime

def lastModifiedFromNow(updated_at, utc=True):
  """현재 시간과 최종 수정일간의 날짜 차이를 계산\n
  [중요!!] UTC 시간을 기준으로 계산이 기본값

  Args:
      updated_at (date)
      utc (bool, optional): utc=False이면 utc zone을 고려하지 않고 현재 timezone을 기준으로 계산

  Returns:
      _type_: _description_
  """
  # mongodb는 utc를 사용하여 시간을 저장하므로 datetime.timedelta(hours=9)을 빼서 시간차를 극복
  past_time = datetime.datetime.now() - updated_at

  if utc:
    past_time = past_time-datetime.timedelta(hours=9)

  return past_time
