import logging
import os
# logging level : DEBUG < INFO < WARNING < ERROR < CRITICAL 
try:
    import codecs
except ImportError:
    codecs = None
import logging.handlers
import time
import os

class MyTimedRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
  def __init__(self,dir_log, when):
   self.dir_log = dir_log
   filename =  self.dir_log+time.strftime("%Y-%m-%d_%H:%M")+".log" #dir_log here MUST be with os.sep on the end
   # FIXME - 현재 backupCount가 작동하지 않는 것 같음, 알아보기
   logging.handlers.TimedRotatingFileHandler.__init__(self,filename, when=when, backupCount=10, encoding="utf-8", interval=10)
  def doRollover(self):
   """
   TimedRotatingFileHandler remix - rotates logs on daily basis, and filename of current logfile is time.strftime("%m%d%Y")+".txt" always
   """ 
   self.stream.close()
   # get the time that this sequence started at and make it a TimeTuple
   t = self.rolloverAt - self.interval
   timeTuple = time.localtime(t)
   self.baseFilename = self.dir_log+time.strftime("%Y-%m-%d_%H:%M")+".log"
   if self.encoding:
     self.stream = codecs.open(self.baseFilename, 'w', self.encoding)
   else:
     self.stream = open(self.baseFilename, 'w')
   self.rolloverAt = self.rolloverAt + self.interval


logger = logging.getLogger("app")

LOGGING_LEVEL = os.getenv("LOGGING_LEVEL")
LOGGING_WHEN = os.getenv("LOGGING_WHEN")


if LOGGING_LEVEL=="DEBUG":
  level = logging.DEBUG
elif LOGGING_LEVEL == "INFO":
  level = logging.INFO
else:
  level = logging.DEBUG
  
logger.setLevel(level)
logger.propagate=False

time_rotating_handler = MyTimedRotatingFileHandler(
  dir_log = "./logs" + os.sep, when=LOGGING_WHEN, 
)
format = logging.Formatter('%(asctime)s [%(name)8s] [%(thread)d] [%(funcName)18s:%(module)14s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

time_rotating_handler.setFormatter(format)
time_rotating_handler.setLevel(level)
time_rotating_handler.namer = lambda name : name + ".log"

console_handler = logging.StreamHandler()
console_handler.setFormatter(format)
console_handler.setLevel(level)
console_handler.namer = lambda name : name + ".log"

logger.addHandler(time_rotating_handler)
logger.addHandler(console_handler)


flask_logger = logging.getLogger("werkzeug")
flask_logger.setLevel(level)
flask_logger.propagate=False
flask_logger.addHandler(time_rotating_handler)
flask_logger.addHandler(console_handler)

def appLogger():
  return logger