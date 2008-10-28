import unittest
from fixtures import *
from plaintypes import *
from fit.ActionFixture import ActionFixture
from engines import Engine

'''
|fit.ActionFixture|
|start|FakeBuyActions|
|check|total|00.00|
|enter|price|12.00|
|press|buy|
|check|total|12.00|
|enter|price|100.00|
|press|buy|
|check|total|112.00|
'''

class FakeBuyActions(object):
    def __init__(self):
        self.arg1 = 0.0
        self.arg2 = 0.0
    def sum(self):
        return self.arg1 + self.arg2

class TestActionFixture(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.loader = CreateFixture(globals())

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_existing_attribute(self):
        wiki = '''
            |ActionFixture|
            |start|FakeBuyActions|
        '''
        
        fixture = self.process(wiki)
