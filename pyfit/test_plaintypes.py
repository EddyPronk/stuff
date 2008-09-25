import unittest
from plaintypes import Cell

class TestCell(unittest.TestCase):
    def test_operators(self):
        self.assertEqual(Cell('bob'), Cell('bob'))
