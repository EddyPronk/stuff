import unittest
from util import *
import inspect
from differ import Differ

class ColumnFixture(object):
    def process(self, table):
        row = table.rows[1]

        desc = []
        for cell in row:
            desc.append(parse_action(str(cell)))

        for row in table.rows[2:]:
            for (d, cell) in zip(desc, row):
                d.apply(self, cell)

class ActionFixture(object):
    def process(self, table):
        #rows = table.rows()
        #row = rows.next()

        for row in table.rows[1:]:
            cells = RowIter(iter(row))
            for cell in cells:
                cell = cells.next()
                f = getattr(self, str(cell))
        
                nargs = len(inspect.getargspec(f)[0]) - 1
                args = cells.get(nargs)
                f(*args)

class DoFixture(object):
    def process(self, table):
        for row in table.rows[1:]:
            cells = RowIter(iter(row))
            name = ''
            args = []
            for cell in cells:
                name += str(cell)
                arg = ''
                try:
                    args.append(str(cells.next()))
                except StopIteration:
                    pass
            f = getattr(self, name)
            f(*args)

class RowFixture(object):
    def collect(self):
        result = self.query()
        out_result = []

        for row in result:
            if type(row) == dict:
                x = [row.get(attr) for attr in self.column_names]
            else:
                x = [getattr(row, attr) for attr in self.column_names]
                
            out_result.append(x)
        return out_result
        
    def process(self, table):
        self.column_names = [str(x) for x in table.rows[1]]
        computed = self.collect()
        expected = table.rows[2:]

        def compare(expected,calculated):
            for e,c in zip(expected, calculated):
                if str(e) != c:
                    e.failed(c)

        self.differ = Differ(compare)
        self.differ.match(expected, computed, 0)

