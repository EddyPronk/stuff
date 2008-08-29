import unittest
from fixtures import *
from table import *

class FakeActionFixture(ActionFixture):

    trace = []
    def amount(self, x):
        self.trace.append(['amount', 'x', x])

    def user(self, userName):
        self.trace.append(['user', 'userName', userName])

    def add(self, x, y):
        self.trace.append(['add', 'x', x, 'y', y])

            
class FakeDoFixture(DoFixture):
    trace = []
    def UserCreatesRoom(self, userName, roomName):
        self.trace.append(['UserCreatesRoom', "userName", userName, "roomName", roomName])

class MarketPicture(object):
    pass
        
class TradingStart(object):
    def __init__(self):
        self.market_picture = {}
        self.market_picture['BHP'] = MarketPicture()

    def run(self):
        pass

def CreateFixture(name):
    return globals()[name]()

class Engine(object):
    def process(self, table):
        name = table.name()
        fixture = CreateFixture(str(name))
        fixture.process(table)
        return fixture

class TestFixtures(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()

    def process(self, wiki):
        return self.engine.process(Table(wiki_table_to_html(wiki)))

    def test_action_fixture(self):
        wiki = '''
            |FakeActionFixture|
            |enter|user  |anna|
            |check|amount|24|
            |check|add   |12|7|
        '''
        
        fixture = self.process(wiki)

        self.assertEqual(fixture.trace[0], ['user', 'userName', 'anna'])
        self.assertEqual(fixture.trace[1], ['amount', 'x', '24'])
        self.assertEqual(fixture.trace[2], ['add', 'x', '12', 'y', '7'])

    def test_do_fixture(self):
        wiki = '''
            |FakeDoFixture|
            |User|anna|Creates|lotr|Room|
        '''
        
        fixture = self.process(wiki)

        self.assertEqual(fixture.trace[0], ['UserCreatesRoom', 'userName', 'anna', 'roomName', 'lotr'])

    def test_market_picture(self):
        
        table = '|TradingStart|'
        name = 'TradingStart'
        fixture = globals()[name]()

        fixture.run()
        li = getattr(fixture, 'market_picture')
        pic = li['BHP']

        table = '|PrepareMarket|BHP|'

        def prepare_market(code):
            pass

        prepare_market('BHP')
        
        table = '''
            |market picture|
            |qty  |bid price|ask price|qty  |
            |1,900|     82.0|83.0     |1,900|
            |  500|     82.0|         |     |
        '''
        
        table = Document(wiki_table_to_html(table))

    def test_dual_header(self):
        table = '''
            |SubmitOrders|
            |bid  |     |ask  |     |
            |qty  |price|price|qty  |
            |1,900| 82.0|83.0 |1,900|
            |  500| 82.0|     |     |
        '''

        table = Table(wiki_table_to_html(table))
        rows = table.rows()
        row = rows.next()
 
        l = []
        for prefix,i in rzip(rows.next(), rows.next()):
            l.append('%s_%s' % (prefix,i))

        self.assertEqual(l, ['bid_qty', 'bid_price', 'ask_price', 'ask_qty'])

    def test_function_names(self):
        t = 'user creates room'
        prefix = 'local'
        words = t.split()
        words.insert(0, prefix)
        f = '_'.join(words)
        self.assertEqual(f, 'local_user_creates_room')


