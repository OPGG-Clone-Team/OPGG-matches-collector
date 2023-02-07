def error_response(error, error_message, error_type, status_code):
  return {
    "message":error_message,
    "error_type":error_type,
    "error_detail":error.__doc__,
  }, status_code
