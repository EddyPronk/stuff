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

class OccupantList(RowFixture):
    def query(self):
        return [ {'user': 'anna', 'room': 'lotr'},
                 {'user': 'luke', 'room': 'lotr'} ]

class OccupantList2(RowFixture):
    def query(self):
        result = []
        
        class Any(object) : pass
        a = Any()
        a.user = 'anna'
        a.room = 'lotr'
        
        result.append(a)
        return result

class TestRowFixture1(unittest.TestCase):

    def test_with_dict(self):
        fixture = OccupantList()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr'], ['luke', 'lotr']])

    def test_with_objects(self):
        fixture = OccupantList2()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr']])

class TestRowFixture2(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_passing_table(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
            |luke |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [])
        self.assertEqual(fixture.differ.surplus, [])

    def test_one_surplus_row(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
            |luke |lotr |
            |bob  |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [[Cell('bob'), Cell('lotr')]])
        self.assertEqual(fixture.differ.surplus, [])

    def test_one_missing_row(self):
        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
        '''

        fixture = self.process(wiki)
        self.assertEqual(fixture.differ.missing, [])
        self.assertEqual(fixture.differ.surplus, [['luke', 'lotr']])
        

