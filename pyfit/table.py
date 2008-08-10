from xml.dom import minidom, Node
#from fixtures import *

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
        self.data.setAttribute("class", "fail")
        expected_value = self.data.childNodes[0].nodeValue
        doc = self.data.ownerDocument
        expected = doc.createElement("span")
        expected.appendChild(doc.createTextNode("expected"))
        expected.setAttribute("class", "fit_label")
        actual = doc.createElement("span")
        actual.appendChild(doc.createTextNode("actual"))
        actual.setAttribute("class", "fit_label")
        hr = doc.createElement("hr")
        hr.appendChild(doc.createTextNode(str(expected_value) + ' '))
        self.data.replaceChild(hr, self.data.childNodes[0])
        value = doc.createTextNode(str(actual_value) + ' ')
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
            while self.data.nextSibling is not None and self.data.nodeType != Node.ELEMENT_NODE:
                self.data = self.data.nextSibling
            if self.data.nodeName != 'td':
                self.data = None
        else:
            self.data = None
        #print cell.data.__dict__
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
        if type(data) is str:
            self.doc = minidom.parseString(data)
            self.data = self.doc.childNodes[0]
        else:
            self.data = data
        

    def rows(self):
        def row_iter(row):
            for row in self.data.childNodes:
                if row.nodeType == Node.ELEMENT_NODE:
                    yield Row(row)
        return row_iter(self.data.childNodes)

    def name(self):
        rows = self.rows()
        row = rows.next()
        it = RowIter(iter(row))
        return str(it.next())

class Document(object):
    def __init__(self, data):
        self.doc = minidom.parseString('<doc>\n' + data + '</doc>\n')
        self.data = self.doc.childNodes[0]

    def html(self):
        html = ''
        for node in self.data.childNodes:
            html += node.toxml()
        return html

    def visit_tables(self):

        for node in self.data.childNodes:
            if node.nodeName == 'table':
                table = Table(node)
                name = table.name()
                module = __import__(name)
                class_ = getattr(module, name)
                fixture = class_()
                #fixture = x(
                fixture.process(table)

