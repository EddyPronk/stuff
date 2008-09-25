import unittest
from plaintypes import Cell
from differ import Differ

def compare(e,c): pass

class TestDiffer(unittest.TestCase):

    def test_two_rows_with_difference(self):
        '''See fitbook Figure 5.3'''
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
