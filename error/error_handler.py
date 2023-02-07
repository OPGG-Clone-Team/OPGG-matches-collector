import traceback
from flask_request_validator import *
from flask_request_validator.error_formatter import demo_error_formatter
from flask_request_validator.exceptions import InvalidRequestError, InvalidHeadersError, RuleError
from error.custom_exception import CustomUserError
from error.response import error_response
from flask_api import status


def error_handle(app):
    """에러 핸들러

    공통 에러 핸들러 추가

    Args:
        app     
        
    Returns:
        json : error_response() 함수로 에러 메시지를 전달해서 반환 받고 return
    """
    
    @app.errorhandler(Exception)
    def handle_error(e):
        traceback.print_exc()
        return error_response(e, "서버 내부 오류가 발생했습니다.", "Unknown Internal Server Error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.errorhandler(AttributeError)
    def handle_error(e):
        traceback.print_exc()
        return error_response(e, "서버 내부 오류가 발생했습니다.", "NoneType Error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.errorhandler(KeyError)
    def handle_key_error(e):
        traceback.print_exc()
        return error_response(e, "서버 내부 오류가 발생했습니다.", "Key Error", status.HTTP_500_INTERNAL_SERVER_ERROR)

    @app.errorhandler(TypeError)
    def handle_type_error(e):
        traceback.print_exc()
        return error_response(e, "서버 내부 오류가 발생했습니다.", "Type Error", status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    @app.errorhandler(ValueError)
    def handle_value_error(e):
        traceback.print_exc()
        return error_response(e, "서버 내부 오류가 발생했습니다.", "Value Error", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @app.errorhandler(InvalidRequestError)
    def handle_data_error(e):
        """validate_params 정규식 에러 (flask_request_validator)
        validate_params rules에 위배될 경우 발생되는 에러 메시지를 처리하는 함수
        """
        traceback.print_exc()
        return error_response(e, "API 명세에 따른 올바른 값을 입력해주세요", "Invalid Request Error",status.HTTP_400_BAD_REQUEST)

    @app.errorhandler(RuleError)
    def handle_rule_error(e):
        traceback.print_exc()
        return error_response(e, "API 명세에 따른 올바른 값을 입력해주세요", "Invalid Rule Error",status.HTTP_400_BAD_REQUEST)
    
    @app.errorhandler(CustomUserError)
    def handle_error(e):
        traceback.print_exc()
        return error_response(e, e.error_message, e.error_type, e.status_code)