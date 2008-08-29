import unittest
from xml.dom import minidom, Node
import re
import sys
import inspect
from table import *
from CalculateDiscount import *
import traceback

class TestTable(unittest.TestCase):

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

    def test_iterator_can_get_first_empty(self):
        html = '<table><tr><td></td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), '')

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

        # instance - marketPicture
        # class    - MarketPicture

        x2(table)

class Engine(object):
    # return the next object in the flow or None.
    # check if fixture has attribute with name of next table.
    # if not create an instance with that name
 
   def process(self, table):
        pass

class TestTable2(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()

    def process(self, table):
        self.engine.process(wiki_table_to_html(table))

    def test_a(self):
        self.process('|TradingStart|')

class ImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Importer(object):
    
    def do_import_module(self, module_name):
        __import__(module_name)

    def import_module(self, name):
        try:
            self.do_import_module(name)
        except Exception, e:
            raise ImportError(traceback.format_exc())

class FakeImporter(Importer):
    def do_import_module(self, name):
        eval('import doesntexist')

if __name__ == '__main__':
    unittest.main()
