import unittest
from fixtures import *
from context import *
from plaintypes import Cell, Table

def CreateFixture(name):
    try:
        type = globals()[name]
    except KeyError, inst:
        raise Exception("Could not create fixture '%s'" % name)
    return type()

class FakeColumnFixture(ColumnFixture):
    arg1 = 0.0
    arg2 = 0.0
    def sum(self):
        return self.arg1 + self.arg2

def wiki_table_to_plain(table):
    output = "<table>"
    rows = []
    for line in table.split('\n'):
        row = line.lstrip().split('|')[1:-1]
        if len(row):
            cells = []
            for cell in row:
                cells.append(Cell(cell.lstrip().rstrip()))
            rows.append(cells)
    output += "</table>"
    return rows

class TestColumnFixture(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture
        pass

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
        self.assertEqual(fixture.arg1, 20.0)
        self.assertEqual(fixture.arg2, 10.0)
        #print self.table.data.toxml()
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
        self.assert_(self.table.cell(2,2).has_failed)
        self.assertEqual(self.table.cell(2,2).actual_value, 30.0)

    def test_passing_test(self):
        wiki = '''
            |FakeColumnFixture|
            |arg1|arg2|sum()|
            |20|10|35|
        '''

        fixture = self.process(wiki)
        self.assert_(self.table.cell(2,2).has_failed)

    def test_non_existing_attribute(self):
        wiki = '''
            |FakeColumnFixture|
            |quantity|
            |20|
        '''

        fixture = self.process(wiki)
        self.assertEqual(self.table.cell(0,2).error_message,
                         """'FakeColumnFixture' object has no attribute 'quantity'""")
        


