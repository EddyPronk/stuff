import unittest
from fixtures import *
from context import *
from plaintypes import *
from ColumnFixture import ColumnFixture
from engines import Engine

def CreateFixture(name):
    try:
        type = globals()[name]
    except KeyError, inst:
        raise Exception("Could not create fixture '%s'" % name)
    return type()

class FakeColumnFixture(ColumnFixture):
    def __init__(self):
        self.arg1 = 0.0
        self.arg2 = 0.0
    def sum(self):
        return self.arg1 + self.arg2

class TestColumnFixture(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_existing_attribute(self):
        wiki = '''
            |FakeColumnFixture|
            |arg1|arg2|sum()|
            |20|10|35|
        '''

        fixture = self.process(wiki)

        # These are float because this is the type in the fixture
        self.assertEqual(fixture.arg1, 20.0)
        self.assertEqual(fixture.arg2, 10.0)

        # These are string
        self.assertEqual(str(self.table.cell(0,2)), '20')
        self.assertEqual(str(self.table.cell(1,2)), '10')
        self.assertEqual(str(self.table.cell(2,2)), '35')

    def test_failing_test(self):
        wiki = '''
            |FakeColumnFixture|
            |arg1|arg2|sum()|
            |20|10|35|
        '''

        fixture = self.process(wiki)
        cell = self.table.cell(2,2)
        self.assert_(cell.has_failed)
        self.assertEqual(cell.actual, 30.0)

    def test_passing_test(self):
        wiki = '''
            |FakeColumnFixture|
            |arg1|arg2|sum()|
            |20|10|35|
        '''

        fixture = self.process(wiki)
        cell = self.table.cell(2,2)
        self.assert_(cell.has_failed)

    def test_non_existing_attribute(self):
        wiki = '''
            |FakeColumnFixture|
            |quantity|
            |20|
        '''

        fixture = self.process(wiki)
        self.assertEqual(self.table.cell(0,2).error_message,
                         """'FakeColumnFixture' object has no attribute 'quantity'""")
        


