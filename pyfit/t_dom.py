import unittest
from xml.dom import minidom, Node
import re
import sys

class Cell(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        def deepest(node):
            if node is not None:
                if node.hasChildNodes():
                    return deepest(node.childNodes[0])
                else:
                    return node
        return deepest(self.data).nodeValue

    def passed(self):
        self.data.setAttribute("class", "pass")

    def failed(self, actual_value):
        expected_value = self.data.childNodes[0].nodeValue
        doc = self.data.ownerDocument
        expected = doc.createElement("span")
        expected.appendChild(doc.createTextNode("expected"))
        expected.setAttribute("class", "fit_label")
        actual = doc.createElement("span")
        actual.appendChild(doc.createTextNode("actual"))
        actual.setAttribute("class", "fit_label")
        hr = doc.createElement("hr")
        hr.appendChild(doc.createTextNode(str(expected_value)))
        self.data.replaceChild(hr, self.data.childNodes[0])
        value = doc.createTextNode(str(actual_value))
        self.data.insertBefore(expected, self.data.childNodes[0])
        self.data.insertBefore(value, self.data.childNodes[0])
        self.data.appendChild(actual)

class RowDomIter(object):
    def __init__(self, data):
        self.data = data
    def __iter__(self):
        return self
    def getn(self, n):
        result = []
        for i in range(0, n):
            result.append(str(it.next()))
        return result
    def next(self):
        if self.data is None:
            raise StopIteration
        cell = Cell(self.data)
        if self.data.nextSibling is not None:
            self.data = self.data.nextSibling
            if self.data.nodeType != Node.ELEMENT_NODE:
                return self.next()
        else:
            self.data = None
        return cell

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

class Row(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return RowDomIter(self.data.childNodes[0])

class Table(object):
    def __init__(self, data):
        self.doc = minidom.parseString(data)
        self.data = self.doc.childNodes[0]

    def rows(self):
        def row_iter(row):
            for row in self.data.childNodes:
                if row.nodeType == Node.ELEMENT_NODE:
                    yield Row(row)
        return row_iter(self.data.childNodes)

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
        setattr(fixture, self.name, type(getattr(fixture, self.name))(str(cell)))

def parse_action(action_desc):
    res = re.search('(.*)\(\)', action_desc)
    if res is not None:
        # funcion_call
        action_name = res.group(1)
        return MethodCall(res.group(1))
    else:
       return SetAttribute(action_desc)

class ColumnFixture(object):
    def process(self, table):
        rows = table.rows()
        row = rows.next()
        row = rows.next()

        desc = []
        for cell in row:
            desc.append(parse_action(str(cell)))

        for row in rows:
            for (d, cell) in zip(desc, row):
                d.apply(self, cell)


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

class TestNew(unittest.TestCase):

    def testSignature(self):
        class FooFixture(object):
            def test_func(self, arg1, arg2):
                self.called = True

        fixture = FooFixture()
        f = getattr(fixture, 'test_func')
        
        import inspect
        self.assert_(inspect.ismethod(f))
        self.assertEqual(2, len(inspect.getargspec(f)[0]) - 1)
        args = [1, 2]
        f(*args)
        self.assert_(fixture.called)

    def test_iterator_can_get_first(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "50.0")

    def test_iterator_can_get_first_text(self):
        html = '<table><tr><td><i>amount</i></td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "amount")
    def test_iterator_can_get_first(self):
        html = '<td><i>amount</i></td>'

    def test_iterator_can_get_second(self):
        html = '<table><tr><td>50.0</td><td>52.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            it.next()
            self.assertEqual(str(it.next()), "52.0")

    def test_iterator_can_get_second_with_extra_text_node(self):
        html = '<table><tr><td>50.0</td>ignore<td>52.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            it.next()
            self.assertEqual(str(it.next()), "52.0")

    def test_iterator_can_stop(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            for cell in row:
                pass

    def test_can_iterate_over_table(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            for col in row:
                self.assertEqual(str(col), "50.0")

    def test_cell_can_pass(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        row = iter(table.rows()).next()
        col = iter(row).next()
        col.passed()
        self.assertEqual('<td class="pass">50.0</td>', col.data.toxml())

    def test_cell_can_fail(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        row = iter(table.rows()).next()
        col = iter(row).next()
        col.failed(49.5)
        self.assertEqual('<td>49.5<span class="fit_label">expected</span><hr>50.0</hr>'
                         '<span class="fit_label">actual</span></td>', col.data.toxml())

    def test_iterator_can_get_n_fields(self):
        html = '<table>' \
            '<tr><td>add</td>' \
            '<td>arg1</td>' \
            '<td>arg2</td>' \
            '</tr>' \
            '</table>'

        table = Table(html)
        row = iter(table.rows()).next()
        it = RowIter(iter(row))
        for cell in it:
            self.assertEqual('add', str(cell))
            self.assertEqual(['arg1', 'arg2'], it.get(2))

    def test_fixture(self):
        html = '<table>' \
            '<tr><td>CalculateDiscount</td></tr>' \
            '<tr><td>amount</td><td>discount()</td></tr>' \
            '<tr><td>1</td><td>4</td></tr>' \
            '<tr><td>2</td><td>5</td></tr>' \
            '<tr><td>3</td><td>6</td></tr>' \
            '</table>'

        table = Table(html)
        rows = table.rows()
        row = rows.next()
        it = RowIter(iter(row))
        name = it.next() 

        fixture = CreateFixture(str(name))
        fixture.process(table)

        self.assertEqual('CalculateDiscount', str(name))
        print table.doc.toxml()

if __name__ == '__main__':
    unittest.main()
