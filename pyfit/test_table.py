import unittest
from xml.dom import minidom, Node
import re
import sys
import inspect
from fixtures import *
from testfixtures import *

class MarketPicture(object):
    pass
        
class TradingStart(object):
    def __init__(self):
        self.market_picture = {}
        self.market_picture['BHP'] = MarketPicture()

    def run(self):
        pass

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


    

class TestNew(unittest.TestCase):

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

    def test_iterator_can_get_first(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "50.0")

    def test_iterator_can_get_first_text(self):
        html = '<table><tr><td>amount</td>\n</tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "amount")

    def test_iterator_can_get_first_text_2(self):
        html = '<table><tr><td><i>amount</i></td>\n</tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "amount")

    def test_iterator_can_get_first(self):
        html = '<td><i>amount</i></td>'
        doc = minidom.parseString(html)
        def deepest(node):
            if node is not None:
                if node.hasChildNodes():
                    return deepest(node.childNodes[0])
                else:
                    return node
        self.assertEqual(deepest(doc).nodeValue, "amount")

            

    def test_iterator_can_get_second(self):
        html = '<table><tr><td>50.0</td><td>52.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            it.next()
            self.assertEqual(str(it.next()), "52.0")

    def test_iterator_can_get_second_with_extra_text_node(self):
        html = '<table><tr><td>50.0</td>ignore<td>52.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            it.next()
            self.assertEqual(str(it.next()), "52.0")

    def test_iterator_can_stop(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            for cell in row:
                pass

    def test_can_iterate_over_table(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            for col in row:
                self.assertEqual(str(col), "50.0")

    def test_cell_can_pass(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        row = iter(table.rows()).next()
        col = iter(row).next()
        col.passed()
        self.assertEqual('<td class="pass">50.0</td>', col.data.toxml())

    def test_cell_can_fail(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        row = iter(table.rows()).next()
        col = iter(row).next()
        col.failed(49.5)
        self.assertEqual('<td class="fail">49.5 <span class="fit_label">expected</span><hr>50.0 </hr>'
                         '<span class="fit_label">actual</span></td>', col.data.toxml())

    def test_iterator_can_get_n_fields(self):
        html = '<table>' \
            '<tr><td>add</td>' \
            '<td>arg1</td>' \
            '<td>arg2</td>\n' \
            '</tr>' \
            '</table>'

        table = Table(html)
        row = iter(table.rows()).next()
        it = RowIter(iter(row))
        s = []
        for cell in it:
            s.append(str(cell))
        self.assertEqual(['add', 'arg1', 'arg2'], s)
        #print s
        it = RowIter(iter(row))
        for cell in it:
            self.assertEqual('add', str(cell))
            self.assertEqual(['arg1', 'arg2'], it.get(2))

    def test_fixture(self):
        html = '<table border="1" cellspacing="0">\n' \
            '<tr><td colspan="2">CalculateDiscount</td>\n' \
            '</tr>\n' \
            '<tr><td><i>amount</i></td>\n' \
            '<td><i>discount()</i></td>' \
            '</tr>\n' \
            '<tr><td>0.00</td>\n' \
            '<td>0.00</td>\n' \
            '</tr>\n' \
            '</table>\n'

        table = Table(html)
        rows = table.rows()
        row = rows.next()
        it = RowIter(iter(row))
        name = it.next() 

        def CreateFixture(name):
            return globals()[name]()

        fixture = CreateFixture(str(name))
        fixture.process(table)

        self.assertEqual('CalculateDiscount', str(name))
        #print table.doc.toxml()

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

    def test_td_with_newline(self):
        # I'm using deepest to get the text out.
        html = '<table><tr><td colspan="2">CalculateDiscount</td>\n</tr></table>'
        table = Table(html)
        self.assertEqual('CalculateDiscount', table.name())

    def test_action_fixture(self):
        html = '<table border="1" cellspacing="0">\n' \
            '<tr><td colspan="2">CalculateDiscount</td>\n' \
            '</tr>\n' \
            '<tr><td><i>amount</i></td>\n' \
            '<td><i>discount()</i></td>' \
            '</tr>\n' \
            '<tr><td>0.00</td>\n' \
            '<td>0.00</td>\n' \
            '</tr>\n' \
            '</table>\n' \
            '\n' \
            '<table border="1" cellspacing="0">\n' \
            '<tr><td colspan="2">CalculateDiscount</td>\n' \
            '</tr>\n' \
            '<tr><td><i>amount</i></td>\n' \
            '<td><i>discount()</i></td>' \
            '</tr>\n' \
            '<tr><td>0.00</td>\n' \
            '<td>0.00</td>\n' \
            '</tr>\n' \
            '</table>\n'

        doc = Document(html)
        doc.visit_tables()
        html = doc.html()
        #print html
        
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
        
        doc = Document(wiki_table_to_html(table))

    def test_flow(self):
        table = [1, 2, 3]
        class Flow(object):
            def first(self, table):
                return self.second

            def second(self, table):
                pass

        f = Flow()

        x1 = f.first
        x2 = x1(table)

        # return the next object in the flow or None.
        # check if fixture has attribute with name of next table.
        # if not create an instance with that name

        # instance - marketPicture
        # class    - MarketPicture

        x2(table)
        

if __name__ == '__main__':
    unittest.main()
