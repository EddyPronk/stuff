import re
import sys
import traceback
import string

class MethodCall(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        f = getattr(fixture, self.name)
        actual = f()
        if actual is None:
            raise Exception('returned None')

        value = str(cell)

        def parse_bool(s):
            return s == 'true'

        if type(actual) is bool:
            if parse_bool(value) == actual:
                cell.passed()
                return
            else:
                cell.failed(actual)
                return
 
        if type(actual)(str(cell)) == actual:
            cell.passed()
        else:
            cell.failed(actual)

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):

        def string_to_bool(s):
            if s == 'true':
                value = True
            else:
                if s == 'false':
                    value = False
            return value
        try:
            old = getattr(fixture, self.name)
            new = str(cell)
            if type(old) is bool:
                setattr(fixture, self.name, string_to_bool(new))
            else:
                setattr(fixture, self.name, type(old)(str(cell)))

        except AttributeError, inst:
            #print e
            cell.error(str(inst))

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        action_name = res.group(1)
        action_name = string.replace(action_name, ' ', '_')
        #return MethodCall(res.group(1))
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
        return self.offset < len(self.data)

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
        __import__(module_name)

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
        return type()
        
def add_to_python_path(path):
    paths =  path.split(':')[:-3] # remove classes:fitnesse.jar:fitlibrary.jar'
    sys.path.extend(paths)

