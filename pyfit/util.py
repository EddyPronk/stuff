import re

class MethodCall(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        f = getattr(fixture, self.name)
        actual = f()
        if type(actual)(str(cell)) == actual:
            cell.passed()
        else:
            cell.failed(actual)

class SetAttribute(object):
    def __init__(self, name):
        self.name = name
    def apply(self, fixture, cell):
        try:
            setattr(fixture, self.name, type(getattr(fixture, self.name))(str(cell)))
        except AttributeError, e:
            cell.error(e)

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        action_name = res.group(1)
        return MethodCall(res.group(1))
    else:
        return SetAttribute(action_desc)

class FileAdapter(object):
    def __init__(self):
        self.data = ''
    def read(self, n):
        print 'read - n [%s]' % n
        result = self.data[0:n]
        #print 'read - result [%s]' % result
        self.data = self.data[n:]
        print 'read - rest [%s]' % self.data
        return result

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


        
