import xml.parsers.expat
import sys
import re

class FakeFile(object):
    def __init__(self):
        self.data = ''
    def write(self, data):
        self.data += data
    def flush(self):
        pass

class Cell:
    def __init__(self):
        self.status = ''
    def set_data(self, data):
        self.data = data
        self.markup_data = data
    
    def passed(self):
        self.status = 'pass'
    def expected(self, value):
        self.status = 'fail'
        self.expected = value

class Table:
    def __init__(self, data, attrs):
        self.attrs = attrs
        self.data = data
    def name(self):
        return self.data[0][0].data
    def format(self):
        for row in self.data:
            for cell in row:
                sys.stdout.write('|')
                t = cell.data
                sys.stdout.write(t + '|')
            sys.stdout.write('\n')

class Parser():
    def __init__(self):
        self.context = None
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.StartElementHandler = self.start_element
        self.parser.EndElementHandler = self.end_element
        self.parser.CharacterDataHandler = self.char_data
        self.rows = []
        self.context = Cell()
        self.markup_data = ''

    def parse(self, document):
        self.parser.Parse("<doc>")
        self.parser.Parse(document)
        self.parser.Parse("</doc>")
        return Table(self.rows, self.table_attrs)
        
    def start_element(self, name, attrs):
        if name == 'table':
            self.table_attrs = attrs
        if name == 'tr':
            self.current_row = []
        elif name == 'td':
            self.markup_data = ''
        else:
            self.markup_data += '<%s>' % name

    def end_element(self, name):
        if name == 'tr':
            self.rows.append(self.current_row)
        elif name == 'td':
            cell = Cell()
            cell.data = self.data
            cell.markup_data = self.markup_data
            self.current_row.append(cell)
        else:
            self.markup_data += '</%s>' % name

    def char_data(self, data):
        if data != '\n':
            self.data = data
            self.markup_data += data

def Parse(html):
    p = Parser()
    return p.parse(html)

def format_cell_html(cell):
    if cell.status == 'pass':
        return '<td class="pass">%s </td>' % cell.data
    elif cell.status == 'fail':
        return '<td class="fail">%s <span class="fit_label">expected</span><hr>%s </hr>' \
               '<span class="fit_label">actual</span></td>' % (cell.data, cell.expected)
    else:
        return '<td>%s </td>' % cell.markup_data

def write_html(os, table):
    os.write('<table')
    for (name, value) in table.attrs.iteritems():
        os.write(' %s="%s"' % (name, value))
    os.write('>')

    for row in table.data:
        os.write('<tr>')
        for cell in row:
            os.write(format_cell_html(cell))
            os.write('\n')
        os.write('</tr>\n')
    os.write('</table>')

    
class MethodCall(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        print 'apply method call'
        print 'name %s' % self.name
        print 'value %s' % cell.data

        f = getattr(fixture, self.name)
        actual = f()
        print 'actual: %s' % actual
        print type(actual)
        print type(cell.data)
        if type(actual)(cell.data) == actual:
            cell.passed()
        else:
            cell.expected(actual)

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        print 'apply set attribute'
        print 'value %s' % cell.data
        setattr(fixture, self.name, type(getattr(fixture, self.name))(cell.data))

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        # funcion_call
        action_name = res.group(1)
        return MethodCall(res.group(1))
    else:
       return SetAttribute(action_desc)

class CalculateDiscountEngine(object):
    def __init__(self):
        pass
    
    def run(self):
        print self.name
        desc = self.table.data[1]
        for row in desc:
            row.action = parse_action(row.data)

        for row in self.table.data[2:]:
            fixture = CreateFixture(self.name)
            for (d, cell) in zip(desc, row):
                sys.stdout.write('|')
                t = cell.data
                sys.stdout.write(d.data + ' ')
                sys.stdout.write(t + '|')
                d.action.apply(fixture, cell)
            sys.stdout.write('\n')

        return 

class ColumnFixture(object):
    pass

class CalculateDiscount(ColumnFixture):

    amount = 0.0

    def discount(self):
        if (self.amount < 0):
            pass
            #throw new RuntimeException("Can't be a negative amount");
        if (self.amount < 1000):
            return 0.0
        else:
            return self.amount*0.05;

def CreateFixture(name):
    object = globals()[name]()
    return object

def CreateFixtureEngine(name, table):
    object = globals()[str(name) + 'Engine']()
    object.name = name
    object.table = table
    return object


