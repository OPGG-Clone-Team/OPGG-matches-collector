import logging
import logging.handlers

# logging level : DEBUG < INFO < WARNING < ERROR < CRITICAL 

def create_handler(config):
  LOGGING_LEVEL = config["LOGGING_LEVEL"]
  LOGGING_WHEN = config["LOGGING_WHEN"]
  
  if LOGGING_LEVEL=="DEBUG":
    level = logging.DEBUG
  elif LOGGING_LEVEL == "INFO":
    level = logging.INFO
  else:
    level = logging.DEBUG

  handler = logging.handlers.TimedRotatingFileHandler(
    filename='./logs/filename.log', when=LOGGING_WHEN
  )
  handler.setLevel(level)
  handler.setFormatter(logging.Formatter('%(asctime)s [%(name)s] [%(funcName)s in %(module)s] - %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
  
  return handler