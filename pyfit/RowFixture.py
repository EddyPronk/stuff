from differ import Differ

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
        for row in self.differ.missing:
            row[0].missing()
        for row in self.differ.surplus:
            table.rows.append(row)
