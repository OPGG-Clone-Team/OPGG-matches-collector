from apscheduler.schedulers.background import BackgroundScheduler


def start_schedule(method, minute):
  schedule = BackgroundScheduler(daemon=True)
  schedule.add_job(method, "interval", minutes = minute, id = "batch", replace_existing=True)
  schedule.start()
    