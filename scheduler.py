from apscheduler.schedulers.background import BackgroundScheduler


def start_schedule(batchList):
  schedule = BackgroundScheduler(daemon=True)

  
  for batch in batchList:
    if batch["method"]=="interval":
      schedule.add_job(batch["method"], "interval", minutes = batch["time"], id = batch["method"].__name__, replace_existing=True)
    # 매일 4시에 돌아가게 변경
    elif batch["method"]=="cron":
      schedule.add_job(batch["method"], "cron", hour = batch["time"], id = batch["method"].__name__, replace_existing=True)
    
  schedule.start()
    