import datetime


def valieSummonerUpdate(updated_at):
  past_time = datetime.datetime.utcnow() - datetime.timedelta(minutes=2)
  if updated_at <= past_time:
    return True
  else:
    return False
  
def timeDifToMinute(updated_at):
  # mongodb는 utc를 사용하여 시간을 저장하므로 datetime.timedelta(hours=9)을 빼서 시간차를 극복
  past_time = datetime.datetime.now() - updated_at - datetime.timedelta(hours=9)
  
  return past_time