import unittest
from xml.dom import minidom, Node
import re
import sys
import inspect
from fixtures import *

class CalculateDiscount(ColumnFixture):

    amount = 0.0

    def discount(self):
        if (self.amount < 0):
            pass
            #throw new RuntimeException("Can't be a negative amount");
        if (self.amount < 1000):
            return 0.0
        else:
            return self.amount*0.05;


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
        self.assertEqual('<td class="fail">49.5<span class="fit_label">expected</span><hr>50.0</hr>'
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

    def test_action_fixture(self):
        html = '<table>' \
            '<tr><td>TestActionFixture</td></tr>' \
            '<tr><td>enter</td><td>user</td><td>anna</td></tr>' \
            '<tr><td>check</td><td>amount</td><td>24</td></tr>' \
            '<tr><td>check</td><td>add</td><td>12</td><td>7</td></tr>' \
            '</table>'

        table = Table(html)
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
        html = '<table>' \
            '<tr><td>TestDoFixture</td></tr>' \
            '<tr><td>User</td><td>anna</td><td>Creates</td><td>lotr</td><td>Room</td></tr>' \
            '</table>'

        table = Table(html)
        rows = table.rows()
        row = rows.next()
        it = RowIter(iter(row))
        name = it.next() 

        def CreateFixture(name):
            return globals()[name]()

        fixture = CreateFixture(str(name))
        fixture.process(table)
        self.assertEqual(fixture.trace[0], ['UserCreatesRoom', 'userName', 'anna', 'roomName', 'lotr'])

    def _test_td_with_newline(self):
        # I'm using deepest to get the text out.
        html = '<table><tr><td colspan="2">CalculateDiscount</td>\n</tr></table>'
        table = Table(html)
        self.assertEqual('CalculateDiscount', table.name())

if __name__ == '__main__':
    unittest.main()
