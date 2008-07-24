import unittest
from functools import partial
from new import *
import sys
import re

class TestNew(unittest.TestCase):

    def testFixtureName(self):
        html = '''<table>
                    <tr><td>FixtureName</td></tr>
                  </table>'''
        table = Parse(html)
        self.assertEqual(table.name(), 'FixtureName')
        #format_html(table)

    def testCellCanBeEmpty(self):
        cell = Cell()
        html = format_cell_html(cell)
        self.assertEqual(html, '<td></td>')

    def testCellCanPass(self):
        cell = Cell()
        cell.passed()
        html = format_cell_html(cell)
        self.assertEqual(html, '<td class="pass"></td>')

    def testCellCanFail(self):
        cell = Cell()
        cell.data = '0.00'
        cell.expected('50.0')
        html = format_cell_html(cell)
        self.assertEqual(html, '<td class="fail">0.00 <span class="fit_label">expected</span><hr>50.0 '
                               '<span class="fit_label">actual</span></td>')

    def testCanFoo(self):
        table = Parse(input)
        table.format()
        
        name = table.name()
        engine = CreateFixtureEngine(name, table)
        engine.run()

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        print 'apply set attribute'
        print 'value %s' % cell.data
        setattr(fixture, self.name, type(getattr(fixture, self.name))(cell.data))

import re
def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        # funcion_call
        action_name = res.group(1)
        return MethodCall(res.group(1))
    else:
       return SetAttribute(action_desc)

class CalculateDiscountEngine(object):
    def __init__(self):
        pass
    
    def run(self):
        print self.name
        desc = self.table.data[1]
        for row in desc:
            row.action = parse_action(row.data)

        for row in self.table.data[2:]:
            fixture = CreateFixture(self.name)
            for (d, cell) in zip(desc, row):
                sys.stdout.write('|')
                t = cell.data
                sys.stdout.write(d.data + ' ')
                sys.stdout.write(t + '|')
                d.action.apply(fixture, cell)
            sys.stdout.write('\n')

        return 

class ColumnFixture(object):
    pass

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

def CreateFixture(name):
    object = globals()[name]()
    return object

def CreateFixtureEngine(name, table):
    object = globals()[str(name) + 'Engine']()
    object.name = name
    object.table = table
    return object

class TestNew(unittest.TestCase):

    def testFixtureName(self):
        html = '''<table>
                    <tr><td>FixtureName</td></tr>
                  </table>'''
        table = Parse(html)
        self.assertEqual(table.name(), 'FixtureName')
        #format_html(table)

    def testCellCanBeEmpty(self):
        cell = Cell()
        cell.set_data("1")
        html = format_cell_html(cell)
        self.assertEqual(html, '<td>1 </td>')

    def testCellCanPass(self):
        cell = Cell()
        cell.data = 1
        cell.passed()
        html = format_cell_html(cell)
        self.assertEqual(html, '<td class="pass">1 </td>')

    def testCellCanFail(self):
        cell = Cell()
        cell.data = '0.00'
        cell.expected('50.0')
        html = format_cell_html(cell)
        self.assertEqual(html, '<td class="fail">0.00 <span class="fit_label">expected</span><hr>50.0 </hr>'
                               '<span class="fit_label">actual</span></td>')

    def testCanFoo(self):
        table = Parse(input)
        #table.format()
        
        name = table.name()
        engine = CreateFixtureEngine(name, table)
        #engine.run()
        
        os = FakeFile()
        write_html(os, table)
        #print os.data
        #print len(os.data)
        
        # <td colspan="2">
        #fixture = CreateFixture(name, table)


        

if __name__ == '__main__':
    unittest.main()

