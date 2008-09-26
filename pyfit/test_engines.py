import unittest
from engines import Engine

class TestEngines(unittest.TestCase):

    def test_action_fixture(self):
        engine = Engine()
        #engine.load_fixture('SomeQuery')

        def importer(text):
            x = compile('import doesntexist\n', 'not_a_file.py', 'exec')
            eval(x)

#print type(engine.fixture)

