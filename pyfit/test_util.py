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

class TestSetAttribute(unittest.TestCase):
    def setUp(self):
        self.engine = Engine()

    def apply(self, fixtureType, name, value):
        operation = SetAttribute(name)
        fixture = fixtureType()
        cell = Cell(value)
        operation.apply(fixture, cell, self.engine)
        return fixture

    def test_assignment(self):
        class FakeFixture(object):
            total = 0.0

        fixture = self.apply(FakeFixture, "total", "12.00")
        self.assertEqual(fixture.total, 12.00)

    def test_setter(self):
        class FakeFixture(object):
            def price(self, currentPrice):
                self.currentPrice = float(currentPrice)

        fixture = self.apply(FakeFixture, "price", "12.00")
        self.assertEqual(fixture.currentPrice, 12.0)

    def test_missing_attribute(self):
        class FakeFixture(object):
            pass

        try:
            fixture = self.apply(FakeFixture, "total", "12.00")
            operation.apply(fixture, cell, self.engine)
        except Exception, inst:
            pass
        self.assertEqual(str(inst), "'FakeFixture' object has no attribute 'total'")

class TestUtil(unittest.TestCase):

    def setUp(self):
        self.engine = Engine()

    def test_set2(self):
        class FakeFixture(object):
            def price(self, currentPrice):
                self.currentPrice = float(currentPrice)

        operation = SetAttribute('price')
        fixture = FakeFixture()
        cell = Cell('12.00')
        operation.apply(fixture, cell, self.engine)
        self.assertEqual(fixture.currentPrice, 12.00)

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

        self.engine.print_traceback = True
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
