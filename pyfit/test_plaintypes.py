import unittest
from plaintypes import Cell, Table

class TestCell(unittest.TestCase):
    def test_operators(self):
        self.assertEqual(Cell('bob'), Cell('bob'))

class TestTable(unittest.TestCase):
    def test_adding_row(self):
        table = Table([[]])
        table.append_row(['anna', 'lotr']) 
        self.assertEqual(table.rows, [ [], ['anna', 'lotr'] ]) 
