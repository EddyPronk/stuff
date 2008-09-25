import unittest
from xml.dom import minidom, Node
import re
import sys
from table import *
from CalculateDiscount import *
from util import *

class TestTable(unittest.TestCase):

    def test_new_table(self):
        wiki = '''
            |zero|
            |one  |1|2|
            |two  |3|4|
            |three|5|6|
        '''
        
        html = wiki_table_to_html(wiki)
        table = Table(html)
        cell = table.rows[2][1]
        cell.passed()
#        x = minidom.parseString(html)
#        t = x.childNodes[0]

        #print rows

    def test_null_table(self):
        html = '<table><tr><td></td></tr></table>'
        table = Table(html)
        self.assertEqual(table.rows[0][0], '')

    def test_can_read_cell(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        self.assertEqual(str(table.rows[0][0]), '50.0')

    def test_can_read_cell_with_newline(self):
        html = '<table><tr><td>amount</td>\n</tr></table>'
        table = Table(html)
        self.assertEqual(str(table.rows[0][0]), 'amount')

    def test_can_read_formatted_text(self):
        html = '<table><tr><td><i>amount</i></td>\n</tr></table>'
        table = Table(html)
        self.assertEqual(str(table.rows[0][0]), 'amount')

    def test_can_get_second(self):
        html = '<table><tr><td>50.0</td><td>52.0</td></tr></table>'
        table = Table(html)
        self.assertEqual(str(table.rows[0][1]), '52.0')
        self.assertEqual(str(table.cell(col=1, row=0)), '52.0')

    def test_can_get_second_with_extra_text_node(self):
        html = '<table><tr><td>50.0</td>ignore<td>52.0</td></tr></table>'
        table = Table(html)
        self.assertEqual(str(table.cell(col=1, row=0)), '52.0')

    def test_can_iterate_over_table(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows:
            for col in row:
                self.assertEqual(str(col), "50.0")

    def test_cell_can_pass(self):
        cell = Cell(minidom.parseString('<td>50.0</td>').childNodes[0])
        cell.passed()
        self.assertEqual('<td class="pass">50.0</td>', cell.data.toxml())

    def test_cell_can_fail(self):
        cell = Cell(minidom.parseString('<td>50.0</td>').childNodes[0])
        cell.failed(49.5)
        self.assertEqual('<td class="fail">49.5 <span class="fit_label">expected</span><hr>50.0 </hr>'
                         '<span class="fit_label">actual</span></td>', cell.data.toxml())

    def test_cell_can_be_missing(self):
        cell = Cell(minidom.parseString('<td>50.0</td>').childNodes[0])
        cell.missing()
        self.assertEqual('<td class="fail">50.0 <span class="fit_label">missing</span></td>',
                         cell.data.toxml())

    def test_cell_can_be_surplus(self):
        cell = Cell(minidom.parseString('<td>50.0</td>').childNodes[0])
        cell.surplus()
        self.assertEqual('<td class="fail">50.0 <span class="fit_label">surplus</span></td>',
                         cell.data.toxml())

    def test_cell_can_have_error(self):
        cell = Cell(minidom.parseString('<td>amount</td>').childNodes[0])
        cell.error('some message')
        self.assertEqual(
            '<td class="error">amount<hr>some message</hr></td>',
            str(cell.data.toxml()))

    def test_adding_row(self):
        html = '<table><tr><td>name</td><td>room</td></tr></table>'
        table = Table(html)
        table.append_row(['anna', 'lotr']) 
        #print table.data.toxml()
        #self.assertEqual(table.rows, [ [], ['anna', 'lotr'] ]) 

    def _test_iterator_can_get_n_fields(self):
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
        rows = table.rows
        #row = rows.next()
        #it = RowIter(iter(row))
        name = table.rows[0][0]

        def CreateFixture(name):
            return globals()[name]()

        fixture = CreateFixture(str(name))
        fixture.process(table)

        self.assertEqual('CalculateDiscount', str(name))
        #print table.doc.toxml()

    def _test_td_with_newline(self):
        html = '<table><tr><td colspan="2">CalculateDiscount</td>\n</tr></table>'
        table = Table(html)
        self.assertEqual('CalculateDiscount', table.name())

    def _test_action_fixture(self):
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
        #doc.visit_tables()
        html = doc.html()
        
    def _test_flow(self):
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

