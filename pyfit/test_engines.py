import unittest
from engines import Engine, StringLoader
from plaintypes import *

class TestEngines(unittest.TestCase):

    def test_loading_non_existing_fixture(self):
        engine = Engine()
        engine.loader = StringLoader('import doesntexist\n')
        try:
            engine.load_fixture('SomeQuery')
        except ImportError, inst:
            pass

        self.assertEqual(str(inst), 'No module named doesntexist')

    def test_action_fixture(self):
        engine = Engine()
        engine.load_fixture('fit.RowFixture')
        engine.load_fixture('fit.ColumnFixture')
        engine.load_fixture('fit.ActionFixture')

    def test_input_table(self):

        engine = Engine()
        engine.loader = StringLoader('import doesntexist\n')

        wiki = '''
            |OccupantList|
            |user |room |
            |anna |lotr |
            |luke |lotr |
        '''

        table = Table(wiki_table_to_plain(wiki))
        engine.process(table, throw=False)

    def test_compare(self):

        engine = Engine()
        cell = Cell('1')
        engine.compare(cell, 1)
        #print cell.__dict__
