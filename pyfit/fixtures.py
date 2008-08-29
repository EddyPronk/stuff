import unittest
from util import *
from table import *
import inspect

class ColumnFixture(object):
    def process(self, table):
        rows = table.rows()
        row = rows.next()
        row = rows.next()

        desc = []
        for cell in row:
            #print 'cell [%s]' % str(cell)
            desc.append(parse_action(str(cell)))

        for row in rows:
            for (d, cell) in zip(desc, row):
                d.apply(self, cell)

class ActionFixture(object):
    def process(self, table):
        rows = table.rows()
        row = rows.next()

        for row in rows:
            cells = RowIter(iter(row))
            for cell in cells:
                cell = cells.next()
                f = getattr(self, str(cell))
        
                nargs = len(inspect.getargspec(f)[0]) - 1
                args = cells.get(nargs)
                f(*args)

class DoFixture(object):
    def process(self, table):
        rows = table.rows()
        row = rows.next()

        for row in rows:
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

