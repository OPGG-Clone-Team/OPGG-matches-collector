from flasgger import Schema, fields
from marshmallow.validate import Length, OneOf
from error.custom_exception import RuleError

class Body(Schema):
  summonerName = fields.String(required=True, validate=Length(min=1, max=40))

  def swag_validation_function(self, data, main_def):
    self.load(data)
    
  def swag_validation_error_handler(self, err, data, main_def):
    raise RuleError('test')