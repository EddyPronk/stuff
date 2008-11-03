from util import *

class ActionFixture(object):
    def process(self, table):
        for row in table.rows[1:]:
            action = str(row[0])
            action = string.replace(action, ' ', '_')
            method = getattr(self, action)
            method(row)

    def start(self, row):
        name = str(row[1])
        self.fixture = self.engine.loader.load(name)

    def enter(self, row):
        cell = row[2]
        name = str(row[1])
        d = SetAttribute(str(row[1]))
        d.apply(self.fixture, cell, self.engine)

    def press(self, row):
        name = str(row[1])
        name = string.replace(name, ' ', '_')
        attribute = getattr(self.fixture, name)
        attribute()

    def check(self, row):
        cell = row[2]
        name = str(row[1])
        name = string.replace(name, ' ', '_')
        d = MethodCall(name)
        d.apply(self.fixture, cell, self.engine)
