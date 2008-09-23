import unittest
from fixtures import *
from context import *

def CreateFixture(name):
    try:
        type = globals()[name]
    except KeyError, inst:
        raise Exception("Could not create fixture '%s'" % name)
    return type()

class FakeColumnFixture(ColumnFixture):
    amount = 0.0

class TestColumnFixture(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture
        pass

    def process(self, wiki):
        self.table = Table(wiki_table_to_html(wiki))
        return self.engine.process(self.table)

    def test_dual_header(self):
        wiki = '''
            |FakeColumnFixture|
            |amountx|
            |20|
        '''

        table = Table(wiki_table_to_html(wiki))
        fixture = self.process(wiki)
        print self.table.data.toxml()
        c = table.cell(0,2)
        print c.data.toxml()
        


