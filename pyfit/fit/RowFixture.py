from differ import Differ
import string

class RowFixture(object):
    def collect(self):
        result = self.query()
        out_result = []

        for row in result:
            if type(row) == dict:
                x = [row.get(attr) for attr in self.column_names]
            else:
                for attr in self.column_names:
                    pass
                    #print string.replace(attr, ' ', '_')
                x = [getattr(row, string.replace(attr, ' ', '_')) for attr in self.column_names]
                
            out_result.append(x)
        return out_result
        
    def process(self, table):
        self.column_names = [str(x) for x in table.rows[1]]
        computed = self.collect()
        expected_values = table.rows[2:]

        def compare_row(expected_values,calculated):
            for expected_value, actual_value in zip(expected_values, calculated):
                self.engine.compare(expected_value, actual_value)

        self.differ = Differ(compare_row)
        self.differ.match(expected_values, computed, 0)
        for row in self.differ.missing:
            row[0].missing()
        for row in self.differ.surplus:
            table.append_row(row)
