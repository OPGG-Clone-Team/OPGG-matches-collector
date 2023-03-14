'''
    dev_error_message : 개발자 에러 메시지
    error_message : 사용자 에러 메시지
    
    class errorClassName(CustomUserError):
        # parameter 설명
        # 두 번째 인자 : user error message 세 번째 인자 : dev error message 
        def __init__(self, error_message, dev_error_message):
            status_code = 500  # 에러코드
            if not dev_error_message :
                dev_error_message = "default error message"
            super().__init__(status_code, dev_error_message, error_message)
'''

from flask_request_validator import AbstractRule
from flask_request_validator.exceptions import RuleError, RequiredJsonKeyError, RequestError
from flask_api import status
from utils.summoner_name import isValidInternalName, makeInternalName
import logging

logger = logging.getLogger("app")

class CustomUserError(Exception):
    def __init__(self, error_message, error_type, status_code):
        self.status_code = status_code
        self.error_type = error_type
        self.error_message = error_message
        
class RateLimiteExceededError(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        self.error_message = error_message
        self.error_type = "Rate Limit Exceeded"
        
class TooManySummonerRequest(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_429_TOO_MANY_REQUESTS
        self.error_message = error_message
        self.error_type = "Trying to update too frequently"

class ForbiddenError(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.error_message = error_message
        self.error_type = "Using forbidden api key"

class DataNotExists(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_message = error_message
        self.error_type = "Data Not Exist"

class SummonerNotExists(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_message = error_message
        self.error_type = "Summoner Not Exist"
        
class RequestDataNotExists(CustomUserError):
    def __init__(self, error_message):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.error_message = error_message
        self.error_type = "Request Data Not Exist"

class ValidateStartIdxParam(AbstractRule):
    def validate(self, value):
        if not 0 <= value <= 200:
            #TODO - 초기 인덱스값 범위 어떻게 할지 - 공식문서 참조
            raise RuleError('startIdx는 0부터 200 사이의 값으로 지정해야 합니다.')
        return value
      
class ValidateSizeParam(AbstractRule):
    def validate(self, value):
        if not 0 <= value <= 200:
            #TODO - size 범위 어떻게 할건지 - 공식문서 참조
            raise RuleError('size는 0부터 200 사이의 값으로 지정해야 합니다.')
        return value

class ValidatePageParam(AbstractRule):
    def validate(self, value):
        if not 0 <= value <= 50:
            #TODO - page 범위 어떻게 할건지 - 공식문서 참조
            raise RuleError('page는 0부터 50 사이의 값으로 지정해야 합니다.')
        return value
    
class ValidateInternalNameParam(AbstractRule):
    def validate(self, value):
        # logger.info(value)
        if not isValidInternalName(value):
            raise RuleError('internalName의 형식에 맞게 데이터를 지정하세요.')
        return makeInternalName(value)

# class IsStr(AbstractRule):
#     def validate(self, value):
#         if not isinstance(value, str):
#             raise RuleError('invalid request')
#         return value

# class IsRequired(AbstractRule):
#     def validate(self, value):
#         if not value:
#             raise RuleError('invalid request')
#         return value
#         if not dev_error_message:
#             dev_error_message = "order status type id doesn't exist"
