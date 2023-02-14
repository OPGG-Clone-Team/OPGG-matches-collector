from apscheduler.schedulers.background import BackgroundScheduler


def start_schedule(batchList):
  schedule = BackgroundScheduler(daemon=True)
  for batch in batchList:
    schedule.add_job(batch["method"], "interval", minutes = batch["time"], id = batch["method"].__name__, replace_existing=True)

  schedule.start()
    