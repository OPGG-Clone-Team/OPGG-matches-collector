def error_response(error, error_message, error_type, status_code):
  response = {
    "message":error_message,
    "error_type":error_type,
  }
  if error.__doc__:
    response["error_detail"]=error.__doc__
    
  return response, status_code
