import unittest
from xml.dom import minidom, Node

input = '''<table border="1" cellspacing="0">
<tr><td colspan="2">CalculateDiscount</td>
</tr>
<tr><td><i>amount</i></td>
<td><i>discount()</i></td>
</tr>
<tr><td>0.00</td>
<td>0.00</td>
</tr>
<tr><td>100.00</td>
<td>0.00</td>
</tr>
<tr><td>999.00</td>
<td>0.00</td>
</tr>
<tr><td>1000.00</td>
<td>0.00</td>
</tr>
<tr><td>1010.00</td>
<td>50.50</td>
</tr>
<tr><td>1100.00</td>
<td>55.00</td>
</tr>
<tr><td>1200.00</td>
<td>60.00</td>
</tr>
<tr><td>2000.00</td>
<td>100.00</td>
</tr>
</table>'''

def deepest(node):
    if node is not None:
        if node.hasChildNodes():
            return deepest(node.childNodes[0])
        else:
            return node


class Cell(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
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

#    def cells(self):
#        def cell_iter(row):
#            for col in row.childNodes:
#                if col.nodeType == Node.ELEMENT_NODE:
#                    e = deepest(col.childNodes[0])
                    #yield e.nodeValue
#                    yield Cell(e)

        return cell_iter(self.data)

class RowIter(object):
    def __init__(self, data):
        self.data = data
    def __iter__(self):
        return self
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

#            if self.data.nextSibling.nodeType == Node.ELEMENT_NODE:

#        if self.data == None:
#            raise StopIteration

#        result = self.data
#    def getn(self, n):
#        result = []
#        for i in range(0, n):
#            result.append(str(it.next()))
#        return result

#        return self.it.next()

class Row(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return RowIter(self.data.childNodes[0])

def Parse(string):
    return minidom.parseString(string)

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

def get_next_cells(c, n):
    result = []
    for i in range(0, n):
        result.append(str(c.next()))
    return result

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

    def testSimpleTable(self):
        html = '<table>' \
            '<tr><td><a href="FooBar">FooBar</a></td>' \
            '<td>1</td>' \
            '<td>2</td>' \
            '<td>Baz</td>' \
            '<td>3</td>' \
            '</tr>' \
            '</table>'

        table = Table(html)
        row = iter(table.rows()).next()
        col = iter(row).next()

        n = 0
        for cell in row:
            n += 1

        self.assertEqual(n, 5)
        self.assertEqual('FooBar', str(col.next()))        
        self.assertEqual(['1','2'], get_next_cells(col, 2))
        self.assertEqual('Baz', str(col.next()))        
        self.assertEqual(['3'], get_next_cells(col, 1))

    def test_iterator_can_get_first(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            self.assertEqual(str(it.next()), "50.0")

    def test_iterator_can_get_second(self):
        html = '<table><tr><td>50.0</td><td>52.0</td></tr></table>'
        table = Table(html)
        for row in table.rows():
            it = iter(row)
            it.next()
            self.assertEqual(str(it.next()), "52.0")

    def test_iterator_can_get_second2(self):
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

    #def testCanIterateOverTable(self):
    #    html = '<table><tr><td>50.0</td></tr></table>'
    #    table = Table(html)
    #    for row in table.rows():
    #        for col in row:
    #            self.assertEqual(str(col), "50.0")

    def testCellCanPass(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        #row = iter(table.rows()).next()
        #col = iter(row).next()
        #col.passed()
        #self.assertEqual('<td class="pass">50.0</td>', col.data.toxml())

    def testCellCanFail(self):
        html = '<table><tr><td>50.0</td></tr></table>'
        table = Table(html)
        
        #col.failed(49.5)
        #self.assertEqual('<td>49.5<span class="fit_label">expected</span><hr>50.0</hr>'
        #                 '<span class="fit_label">actual</span></td>', col.data.toxml())

    def testSimpleTable(self):
        html = '<table>' \
            '<tr><td>user</td>' \
            '<td>anna</td>' \
            '<td>room</td>' \
            '<td>lotr</td>' \
            '</tr>' \
            '</table>'

        class RowReader(object):
            def __init__(self, row):
                self.data = iter(row)
                self.eof_state = False
            def read(self):
                try:
                    value = self.data.next()
                    return value
                except StopIteration:
                    self.eof_state = True
            def readcells(self, n):
                result = []
                for i in range(0, n):
                    result.append(str(self.read()))
                return result
                    
            def eof(self):
                return self.eof_state

        table = Table(html)
        for row in table.rows():
            pass
            #it = my_iter(row)
            #for cell in it:
            #    print cell
            #    print it.getn(2)

if __name__ == '__main__':
    unittest.main()
