from xml.dom import minidom, Node

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

