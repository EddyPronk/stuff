import unittest
from util import *
from plaintypes import *

class TestUtil(unittest.TestCase):
    def test_if_apply_throws_when_function_returns_None(self):

        class FakeFixture(object):
            def func(self):
                pass

        operation = MethodCall('func')
        fixture = FakeFixture()
        cell = Cell('dummy')
        try:
            operation.apply(fixture, cell)
        except Exception, inst:
            pass
        self.assertEqual(str(inst), 'returned None')

    def test_2(self):

        class FakeFixture(object):
            def func(self):
                return False

        operation = MethodCall('func')
        fixture = FakeFixture()
        cell = Cell('false')
        operation.apply(fixture, cell)
        self.assertEqual(cell.has_passed, True)

    def test_3(self):
        
        def parse_bool(s):
            return s is 'true'

        self.assertEqual(True, parse_bool('true'))
        self.assertEqual(False, parse_bool('false'))

        def bool_to_string(s):
            return str(s).lower()

        self.assertEqual('true',  bool_to_string(True))
        self.assertEqual('false', bool_to_string(False))

    def test_4(self):
        class FakeFixture(object):
            reliable = False

        operation = SetAttribute('reliable')
        fixture = FakeFixture()
        cell = Cell('false')
        operation.apply(fixture, cell)
        self.assertEqual(fixture.reliable, False)

        class Bool(object):
            def parse(self, s):
                if s == 'true':
                    value = True
                else:
                    if s == 'false':
                        value = False
                    else:
                        raise Exception("Can't convert `%s`" % s)
                return value

        converter = Bool()
        converter.parse('false')
