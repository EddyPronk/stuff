import unittest
from fixtures import *
from table import *
from context import *
import traceback

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
    try:
        type = globals()[name]
    except KeyError, inst:
        raise Exception("Could not create fixture '%s'" % name)
    return type()

class Two(object):
    def process(self, table):
        pass
    
class First(object):
    def process(self, table):
        pass

    def Second(self):
        return Two()

class TestFixtures(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()
        self.engine.FixtureFactory = CreateFixture

    def process(self, wiki):
        return self.engine.process(Table(wiki_table_to_html(wiki)))

    def testSignature(self):
        class FooFixture(object):
            def test_func(self, arg1, arg2):
                self.called = True

        fixture = FooFixture()
        f = getattr(fixture, 'test_func')
        
        self.assert_(inspect.ismethod(f))
        self.assertEqual(2, len(inspect.getargspec(f)[0]) - 1)
        args = [1, 2]
        f(*args)
        self.assert_(fixture.called)

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

    def test_if_fails_if_fixture_doesnt_exist(self):
        try:
            fixture = self.process('|NoneExisting|')
        except Exception, inst:
            pass
        
        self.assertEqual(str(inst), "Could not create fixture 'NoneExisting'")

    def test_flow_mode(self):
        fixture = self.process('|First|')
        fixture = self.process('|Second|')
        self.assertEqual(type(fixture), Two)

    def test_flow_mode2(self):
        fixture = self.process('|First|')
        fixture = self.process('|FakeActionFixture|')
        self.assertEqual(type(fixture), FakeActionFixture)

    def test_collumn_group_fixture(self):

        wiki = '''
            |FakeCollumnFixture|
            |outgoing |      |       |incoming |        |
            |code     | qty  | price |status   | filled |
            |BHP      | 5000 | 41.3  |New      | 4000   |
            |ANZ      | 9000 | 16.1  |New      | 7000   |
        '''

        table = Table(wiki_table_to_html(wiki))
        rows = table.rows()
        row = rows.next()
 
        l = []

        class SetGroupAttribute(object):
            def __init__(self, name, group):
                self.name = name
                self.group = group
            def apply(self, fixture, cell):
                print 'set %s.%s to value [%s]' % (self.group, self.name, cell)
                group = getattr(fixture, self.group)
                setattr(group, self.name, str(cell))

        class GroupCollumnFixture(object):

            def __init__(self):
                pass

            def process(self, table):
                self.desc = []

                group_iter = iter(rows.next())
                coll_iter = iter(rows.next())
                coll = str(coll_iter.next())
                group = str(group_iter.next())
                self.element(group,coll)
                for cell in group_iter:
                    group_name = str(cell)
                    coll = coll_iter.next()        
                    if group_name is not '':
                        self.group_done(group)
                        group = group_name
                    self.element(group,str(coll))
                self.group_done(group)

                for row in rows:
                    for (d, cell) in zip(self.desc, row):
                        d.apply(self, cell)


            def element(self, x,y):
                print (x,y)
                attr = getattr(self, x)
                self.desc.append(SetGroupAttribute(y,x))
                # need partials here.
                #setattr(attr, y, 'foo')

            def group_done(self, group):
                f = getattr(self, '%s_done' % group)
                f()

        class FakeGroupCollumnFixture(GroupCollumnFixture):
            class Message(object) : pass

            def __init__(self):
                self.outgoing = self.Message()
                self.outgoing.code = 'BHP'

            def outgoing_done(self):
                self.incoming = self.Message()
                print self.outgoing.__dict__

            def incoming_done(self):
                pass

        fixture = FakeGroupCollumnFixture()
        fixture.process(table)

