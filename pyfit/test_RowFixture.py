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

class OccupantList1(RowFixture):
    
    def query(self):
        result = []
        
        class Any(object) : pass
        a = Any()
        a.user = 'anna'
        a.room = 'lotr'
        
        result.append(a)
        return result

class OccupantList2(RowFixture):
    
    def query(self):
        result = []
        
        a = {'user': 'anna', 'room': 'lotr'}
        
        result.append(a)
        return result

class TestRowFixture1(unittest.TestCase):

    def test_with_objects(self):
        fixture = OccupantList1()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr']])

    def test_with_dict(self):
        fixture = OccupantList2()
        fixture.column_names = ['user', 'room']
        result = fixture.collect()
        self.assertEqual(result, [['anna', 'lotr']])

class TestRowFixture2(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture
        pass

    def process(self, wiki):
        self.table = Table(wiki_table_to_plain(wiki))
        return self.engine.process(self.table)

    def test_existing_attribute(self):
        wiki = '''
            |OccupantList1|
            |user |room |
            |anna |lotr |
            |luke |lotr |
        '''

        fixture = self.process(wiki)
        
class Differ(object):
    def __init__(self, compare):
        self.compare = compare
        self.missing = []
        self.surplus = []

    def match(self, expected, computed, col):
        if col >= 2:
            self.check(expected, computed)
        else:
            self.keyMap = {}
            self.ePartition(expected, col, self.keyMap)
            self.cPartition(computed, col, self.keyMap)
            for key, value in self.keyMap.items():
                eList, cList = value
                if not eList:
                    self.surplus.extend(cList)
                elif not cList:
                    self.missing.extend(eList)
                elif (len(eList) == 1 and len(cList) == 1):
                    self.check(eList, cList)
                else:
                    self.match(eList, cList, col+1)

    def ePartition(self, rows, col, map):
        for row in rows:
            key = str(row[0])
            self.insureKeyExists(map, key)
            map[key][0].append(row)

    def cPartition(self, rows, col, map):
        for row in rows:
            key = row[0]
            self.insureKeyExists(map, key)
            map[key][1].append(row)

    def insureKeyExists(self, map, key):
        if map.has_key(key):
            return
        map[key] = [[], []]

    def check (self, eList, cList):
        for e,c in zip(eList, cList):
            self.compare(e,c)

def compare(e,c):
    pass

class TestTableDiff(unittest.TestCase):

    def test_two_rows_with_difference(self):
        computed = [['anna', 'lotr'],
                    ['luke', 'lotr']]
        expected = [[Cell('anna'), Cell('shrek')],
                    [Cell('luke'), Cell('lotr')]]
        
        def compare(expected,calculated):
            for e,c in zip(expected, calculated):
                if str(e) != c:
                    e.failed(c)

        differ = Differ(compare)
        differ.match(expected, computed, 0)
        cell = expected[0][1]
        self.assertEqual(cell.expected, 'shrek')
        self.assertEqual(cell.actual,   'lotr')

    def test_one_missing(self):
        computed = [['anna', 'lotr']]
        expected = [['anna', 'shrek'],
                    ['luke', 'lotr']]
        
        differ = Differ(compare)
        differ.match(expected, computed, 0)
        self.assertEqual(differ.missing, [['luke', 'lotr']])
        self.assertEqual(differ.surplus, [])

    def test_one_surplus_row(self):
        computed = [['anna', 'lotr'],
                    ['luke', 'lotr']]
        expected = [['anna', 'shrek']]
        
        differ = Differ(compare)
        differ.match(expected, computed, 0)
        self.assertEqual(differ.missing, [])
        self.assertEqual(differ.surplus, [['luke', 'lotr']])
