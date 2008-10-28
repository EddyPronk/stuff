import unittest
from util import *
from plaintypes import *
from engines import Engine

class TestMethodCall(unittest.TestCase):
    def setUp(self):
        class FakeFixture(object):
            def func(self):
                return 1
        self.fixture = FakeFixture()
        self.engine = Engine()

    def test_if_summary_is_initialised(self):
        self.assertEqual(self.engine.summary.right, 0)

    def test_if_cell_can_pass(self):
        operation = MethodCall('func')
        cell = Cell('1')
        operation.apply(self.fixture, cell, self.engine)
        self.assertEqual(cell.has_passed, True)
        self.assertEqual(self.engine.summary.right, 1)

    def test_if_cell_can_pass_twice(self):
        operation = MethodCall('func')
        cell = Cell('1')
        operation.apply(self.fixture, cell, self.engine)
        operation.apply(self.fixture, cell, self.engine)
        self.assertEqual(cell.has_passed, True)
        self.assertEqual(self.engine.summary.right, 2)

class TestUtil(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()

    def test_if_apply_throws_when_function_returns_None(self):
        operation = MethodCall('func')
        class FakeFixture(object):
            def func(self):
                return False
        fixture = FakeFixture()
        cell = Cell('false')

        operation.apply(fixture, cell, self.engine)
        self.assertEqual(cell.has_passed, True)


        class FakeFixture(object):
            def func(self):
                pass

        operation = MethodCall('func')
        fixture = FakeFixture()
        cell = Cell('dummy')
        try:
            operation.apply(fixture, cell, self.engine)
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

        operation.apply(fixture, cell, self.engine)
        self.assertEqual(cell.has_passed, True)

    def test_bool_adapter_2(self):
        class FakeFixture(object):
            reliable = False

        operation = SetAttribute('reliable')
        fixture = FakeFixture()
        cell = Cell('false')
        operation.apply(fixture, cell, self.engine)
        self.assertEqual(fixture.reliable, False)

    def test_list_adapter(self):
        class FakeFixture(object):
            phones = []

        operation = SetAttribute('phones')
        fixture = FakeFixture()
        cell = Cell('(209)373 7453, (209)373 7454')
        operation.apply(fixture, cell, self.engine)
        self.assertEqual(fixture.phones, ['(209)373 7453', '(209)373 7454'])
