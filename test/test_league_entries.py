import unittest
from modules import league_entries
from app import create_app

class UnitTest(unittest.TestCase):
  '''
    league_entries 잘 가져와지는지 확인
  '''
  def setUp(self):
    self.app = create_app()
    
  def update_test(self):
    league_entries.update_all()