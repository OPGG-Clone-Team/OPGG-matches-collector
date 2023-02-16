import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

class Config:
  # DEFAULT CONFIG
  API_KEY=os.environ.get("RIOT_API_KEY_1")
  LOGGING_LEVEL = os.environ.get("LOGGING_LEVEL")
  LOGGING_WHEN = os.environ.get("LOGGING_WHEN")
class DevelopmentConfig(Config):
    # FLASK_ENV = development
    DEBUG=True
    MONGO_HOST =os.environ.get("DEV_MONGO_HOST")
    MONGO_PORT= os.environ.get("DEV_MONGO_PORT")
    MONGO_USERNAME= os.environ.get("DEV_MONGO_USERNAME")
    MONGO_PASSWORD= os.environ.get("DEV_MONGO_PASSWORD")
    MONGO_ADMIN_DB=os.environ.get("DEV_MONGO_ADMIN_DB")
    MONGO_URI=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_ADMIN_DB}"
    FLASK_PORT=os.environ.get("DEV_FLASK_PORT")
    FLASK_HOST=os.environ.get("DEV_FLASK_HOST")
    FLASK_DEBUG = os.environ.get("DEV_FLASK_DEBUG")

class ProductionConfig(Config):
  # FLASK_ENV = production
  # TODO - 구체적인 시스템 설계단계 끝나기 전까지는 debug 모드로 작동
    DEBUG = True
    MONGO_HOST =os.environ.get("MONGO_HOST")
    MONGO_PORT= os.environ.get("MONGO_PORT")
    MONGO_USERNAME= os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD= os.environ.get("MONGO_PASSWORD")
    MONGO_ADMIN_DB=os.environ.get("MONGO_ADMIN_DB")
    MONGO_URI=f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_ADMIN_DB}"
    FLASK_PORT=os.environ.get("FLASK_PORT")
    FLASK_HOST=os.environ.get("FLASK_HOST")

class TestConfig(Config):
    # 테스트 환경, FLASK_ENV = test
    DEBUG=True
    MONGO_HOST =os.environ.get("MONGO_HOST")
    MONGO_PORT= os.environ.get("MONGO_PORT")
    MONGO_USERNAME= os.environ.get("MONGO_USERNAME")
    MONGO_PASSWORD= os.environ.get("MONGO_PASSWORD")
    MONGO_ADMIN_DB=os.environ.get("MONGO_ADMIN_DB")
    # 임시로 세팅
    MONGO_URI=f"mongodb://{MONGO_HOST}:{MONGO_PORT}"
    FLASK_PORT=os.environ.get("FLASK_PORT")
    FLASK_HOST=os.environ.get("FLASK_HOST")
    FLASK_DEBUG = os.environ.get("FLASK_DEBUG")


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "test": TestConfig,
    "default": DevelopmentConfig,
}