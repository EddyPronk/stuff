from util import *

class ColumnFixture(object):
    def process(self, table):
        row = table.rows[1]

        desc = []
        for cell in row:
            desc.append(parse_action(str(cell)))

        for row in table.rows[2:]:
            for (d, cell) in zip(desc, row):
                d.apply(self, cell, self.adapters)
