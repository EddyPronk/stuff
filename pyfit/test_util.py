import unittest
from util import *
from plaintypes import *

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.adapters = DefaultAdapters()

    def test_if_apply_throws_when_function_returns_None(self):

        class FakeFixture(object):
            def func(self):
                pass

        operation = MethodCall('func')
        fixture = FakeFixture()
        cell = Cell('dummy')
        try:
            operation.apply(fixture, cell, self.adapters)
        except Exception, inst:
            pass
        self.assertEqual(str(inst), 'returned None')

    def test_bool_adapter_1(self):

        class FakeFixture(object):
            def func(self):
                return False

        operation = MethodCall('func')
        fixture = FakeFixture()
        cell = Cell('false')

        operation.apply(fixture, cell, self.adapters)
        self.assertEqual(cell.has_passed, True)

    def test_bool_adapter_2(self):
        class FakeFixture(object):
            reliable = False

        operation = SetAttribute('reliable')
        fixture = FakeFixture()
        cell = Cell('false')
        operation.apply(fixture, cell, self.adapters)
        self.assertEqual(fixture.reliable, False)

    def test_list_adapter(self):
        class FakeFixture(object):
            phones = []

        operation = SetAttribute('phones')
        fixture = FakeFixture()
        cell = Cell('(209)373 7453, (209)373 7454')
        operation.apply(fixture, cell, self.adapters)
        self.assertEqual(fixture.phones, ['(209)373 7453', '(209)373 7454'])
