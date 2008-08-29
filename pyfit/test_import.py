import unittest

import sys
import traceback

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
            tb = traceback.format_exc()
            lines = tb.split('\n')
            str = '\n' + lines[0] + '\n' + '\n'.join(lines[5:])
            raise ImportError(str)

class FakeImporter(Importer):
    def do_import_module(self, name):
        x = compile('import doesntexist\n', 'not_a_file.py', 'exec')
        eval(x)
        

class TestImport(unittest.TestCase):

    def test_backtrace(self):
        imp = FakeImporter()
        try:
            result = imp.import_module('dummy')
        except Exception, inst:
            #print inst.value
            pass

        self.assertEqual(inst.value, \
                             '\n'
                             'Traceback (most recent call last):\n' \
                             '  File "not_a_file.py", line 1, in <module>\n' \
                             'ImportError: No module named doesntexist\n')

