from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger("app")
print(logger.getEffectiveLevel)

def start_schedule(batchList):
  schedule = BackgroundScheduler(daemon=True, timezone = 'Asia/Seoul')
  
  logger.info("스케줄러 로드")
  logger.info("1")
  logger.info("2")
  logger.info("3")
  
  for batch in batchList:
    if batch["method"]=="interval":
      schedule.add_job(batch["job"], "interval", minutes = batch["time"], id = batch["job"].__name__, replace_existing=False)
    # 매일 4시에 돌아가게 변경
    elif batch["method"]=="cron":
      schedule.add_job(batch["job"], "cron", hour = batch["time"], id = batch["job"].__name__, replace_existing=True)
  
  schedule.start()
    