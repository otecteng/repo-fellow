import unittest
from repofellow.parser import Parser
from repofellow.injector import Developer
import re
class TestParser(unittest.TestCase):
    def test_commit_rules(self):
        message = "[xxxi] #XXX-112 feat: hello world"
        pattern = r'(.*)#(.*)\s+(.*):\s+(.*?)' 
        self.assertIsNotNone(re.match(pattern, message, flags=0))
