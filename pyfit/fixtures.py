from util import *
import inspect
from differ import Differ

class ActionFixture(object):
    def process(self, table):
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
