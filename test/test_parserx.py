import unittest
from repofellow.parser import Parser
from repofellow.injector import Developer

class TestParser(unittest.TestCase):

    def test_json_to_db(self):
        print("com!")
        data =     [{
        "login": "ghost",
        "id": 1,
        }]
        print(Parser.json_to_db(data,Developer))
 
        # self.assertEqual(d.key, 'value')
