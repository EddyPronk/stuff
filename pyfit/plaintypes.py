class Cell(object):
    def __init__(self, data):
        self.expected = data
        self.has_passed = False

    def __repr__(self):
        return self.expected

    def __eq__(self, other):
        return self.expected == other #.expected

    def passed(self):
        self.has_passed = True

    def failed(self, actual):
        self.has_failed = True
        self.actual = actual

    def error(self, message):
        self.error_message = message

    def missing(self):
        self.is_missing = True

class Table(object):
    def __init__(self, rows):
        self.rows = rows

    def cell(self, col, row):
        return self.rows[row][col]

    def name(self):
        return str(self.rows[0][0])

    def append_row(self, row):
        self.rows.append(row)

def wiki_table_to_plain(table):
    rows = []
    for line in table.split('\n'):
        row = line.lstrip().split('|')[1:-1]
        if len(row):
            cells = []
            for cell in row:
                cells.append(Cell(cell.lstrip().rstrip()))
            rows.append(cells)
    return rows

