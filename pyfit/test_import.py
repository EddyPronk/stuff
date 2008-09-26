import unittest
import sys
import traceback
from util import *

class FakeImporter(Importer):
    def do_import_module(self, name):
        x = compile('import doesntexist\n', 'not_a_file.py', 'exec')
        eval(x)
        

class TestImport(unittest.TestCase):

    def test_backtrace(self):
        imp = FakeImporter()
        try:
            result = imp.import_module('dummy')
        except ImportError, inst:
            #print inst.value
            pass

        self.assertEqual(inst.value, \
                             '\n'
                             'Traceback (most recent call last):\n' \
                             '  File "not_a_file.py", line 1, in <module>\n' \
                             'ImportError: No module named doesntexist\n')

