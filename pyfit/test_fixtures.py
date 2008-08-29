import unittest
from fixtures import *

class TestActionFixture(ActionFixture):

    trace = []
    def amount(self, x):
        self.trace.append(['amount', 'x', x])

    def user(self, userName):
        self.trace.append(['user', 'userName', userName])

    def add(self, x, y):
        self.trace.append(['add', 'x', x, 'y', y])

            
class TestDoFixture(DoFixture):
    trace = []
    def UserCreatesRoom(self, userName, roomName):
        self.trace.append(['UserCreatesRoom', "userName", userName, "roomName", roomName])

class TestFixtures(unittest.TestCase):
    def test_action_fixture2(self):
        table = '''
            |TestActionFixture|
            |enter|user  |anna|
            |check|amount|24|
            |check|add   |12|7|
        '''
        
        table = Table(wiki_table_to_html(table))
        rows = table.rows()
        row = rows.next()
        it = RowIter(iter(row))
        name = it.next() 

        def CreateFixture(name):
            return globals()[name]()

        fixture = CreateFixture(str(name))
        fixture.process(table)
        self.assertEqual(fixture.trace[0], ['user', 'userName', 'anna'])
        self.assertEqual(fixture.trace[1], ['amount', 'x', '24'])
        self.assertEqual(fixture.trace[2], ['add', 'x', '12', 'y', '7'])

    def test_do_fixture(self):
        table = '''
            |TestDoFixture|
            |User|anna|Creates|lotr|Room|
        '''
        
        table = Table(wiki_table_to_html(table))
        rows = table.rows()
        row = rows.next()
        it = RowIter(iter(row))
        name = it.next() 

        def CreateFixture(name):
            return globals()[name]()

        fixture = CreateFixture(str(name))
        fixture.process(table)
        self.assertEqual(fixture.trace[0], ['UserCreatesRoom', 'userName', 'anna', 'roomName', 'lotr'])

