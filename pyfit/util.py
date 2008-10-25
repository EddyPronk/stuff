import re
import sys
import traceback
import string

class BoolAdapter(object):
    def parse(self, s):
        if s == 'true':
            value = True
        else:
            if s == 'false':
                value = False
            else:
                raise Exception("Can't convert `%s`" % s)
        return value

    def convert(self, s):
        return s == 'true'

class ListAdapter(object):
    def parse(self, s):
        return [x.lstrip() for x in s.split(',')]

class MethodCall(object):
    def __init__(self, name):
        self.name = name

    def apply(self, fixture, cell, adapters):
        f = getattr(fixture, self.name)
        actual = f()
        if actual is None:
            raise Exception('returned None')

        value = str(cell)
        target_type = type(actual)
        if adapters.has_key(target_type):
            adapter = adapters[target_type]
            expected = adapter.convert(value)
        else:
            expected = type(actual)(str(cell))

        if expected == actual:
            cell.passed()
        else:
            cell.failed(actual)

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell, adapters):

        try:
            old = getattr(fixture, self.name)
            target_type = type(old)
            cell_value = str(cell)
            if adapters.has_key(target_type):
                adapter = adapters[target_type]
                new = adapter.parse(cell_value)
            else:
                new = type(old)(str(cell))
            setattr(fixture, self.name, new)

        except AttributeError, inst:
            cell.error(str(inst))

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        action_name = res.group(1)
        action_name = string.replace(action_name, ' ', '_')
        return MethodCall(action_name)
    else:
        return SetAttribute(action_desc)

class FileAdapter(object):
    def __init__(self, data):
        self.data = data
        self.offset = 0
    def read(self, n):
        end = self.offset + n
        block = self.data[self.offset:end]
        self.offset = end
        return block
    def eof(self):
        return self.offset >= len(self.data)

def format_10_digit_number(n):
    return "%010i" % n

def wiki_table_to_html(table):
    output = "<table>"
    for line in table.split('\n'):
        row = line.lstrip().split('|')[1:-1]
        if len(row):
            output += "<tr>"
            for cell in row:
                output += "<td>%s</td>\n" % cell.lstrip().rstrip()
            output += "</tr>\n"
    output += "</table>"
    return output

def rzip(a,b):
    prev = ''
    for x,y in zip(a,b):
        if x == '':
            x = prev
        prev = x
        yield (x,y)

class RowIter(object):
    def __init__(self, iter):
        self.iter = iter
    def __iter__(self):
        return self
    def next(self):
        return self.iter.next()
    def get(self, n):
        result = []
        for i in range(0, n):
            result.append(str(self.next()))
        return result

def print_table(table):
    print
    for row in table:
        print '|' + '|'.join([str(x) for x in row]) + '|'

class ImportError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Importer(object):
    def do_import_module(self, module_name):
        pass
        #__import__(module_name)

    def import_module(self, name):
        try:
            self.do_import_module(name)
        except Exception, e:
            tb = traceback.format_exc()
            lines = tb.split('\n')
            str = '\n' + lines[0] + '\n' + '\n'.join(lines[5:])
            raise ImportError(str)

class CreateFixture(object):
    def __init__(self, globals):
        self.globals = globals

    def load(self, name):
        try:
            type = self.globals[name]
        except KeyError, inst:
            raise Exception("Could not create fixture '%s'" % name)
        fixture = type()
        fixture.adapters = {}
        return fixture
        
def add_to_python_path(path):
    paths =  path.split(':')[:-3] # remove classes:fitnesse.jar:fitlibrary.jar'
    sys.path.extend(paths)

def DefaultAdapters():
    adapters = {}
    adapters[bool] = BoolAdapter()
    adapters[list] = ListAdapter()
    return adapters
