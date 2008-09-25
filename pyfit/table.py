from xml.dom import minidom, Node

def create_table(domtree):
    rows = []
    for row in domtree.childNodes:
        if row.nodeName == 'tr':
            row_cells = []
            for cell in row.childNodes:
                if cell.nodeName == 'td':
                    if cell.hasChildNodes():
                        try:
                            c = cell.childNodes[0]
                            row_cells.append(Cell(cell))
                        except IndexError, inst:
                            print cell.__dict__
                            print inst
                    else:
                        row_cells.append('')
            rows.append(row_cells)
    return rows

class Cell(object):
    def __init__(self, data):
        self.data = data
    def __repr__(self):
        def deepest(node):
            if node is not None:
                if node.hasChildNodes():
                    return deepest(node.childNodes[0])
                else:
                    return node
        d = deepest(self.data).nodeValue
        if d == None:
            return ''
        return d

    def passed(self):
        self.data.setAttribute("class", "pass")

    def failed(self, actual_value):
        self.data.setAttribute("class", "fail")
        expected_value = self.data.childNodes[0].nodeValue
        doc = self.data.ownerDocument
        expected = doc.createElement("span")
        expected.appendChild(doc.createTextNode("expected"))
        expected.setAttribute("class", "fit_label")
        span = doc.createElement("span")
        span.appendChild(doc.createTextNode("actual"))
        span.setAttribute("class", "fit_label")
        hr = doc.createElement("hr")
        hr.appendChild(doc.createTextNode(str(expected_value) + ' '))
        self.data.replaceChild(hr, self.data.childNodes[0])
        value = doc.createTextNode(str(actual_value) + ' ')
        self.data.insertBefore(expected, self.data.childNodes[0])
        self.data.insertBefore(value, self.data.childNodes[0])
        self.data.appendChild(span)

    def error(self, message):
        self.data.setAttribute("class", "error")
        doc = self.data.ownerDocument
        hr = doc.createElement("hr")
        hr.appendChild(doc.createTextNode(str(message)))
        value = doc.createTextNode(self.data.childNodes[0].nodeValue)
        self.data.replaceChild(hr, self.data.childNodes[0])
        self.data.insertBefore(value, self.data.childNodes[0])

    def missing(self):
        self.mark('missing')

    def surplus(self):
        self.mark('surplus')

    def mark(self, text):
        doc = self.data.ownerDocument
        self.data.childNodes[0].nodeValue += ' '
        self.data.setAttribute("class", "fail")
        span = doc.createElement("span")
        span.appendChild(doc.createTextNode(text))
        span.setAttribute("class", "fit_label")
        self.data.appendChild(span)

class OldCell(object):
    def __init__(self, data):
        self.data = data

    def __str__(self):
        def deepest(node):
            if node is not None:
                if node.hasChildNodes():
                    return deepest(node.childNodes[0])
                else:
                    return node
        d = deepest(self.data).nodeValue
        if d == None:
            return ''
        return d


class RowDomIter__(object):
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
 
        self.rows = create_table(self.data)
       
    def cell(self, col, row):
        return self.rows[row][col]

    def rows__(self):
        def row_iter(row):
            for row in self.data.childNodes:
                if row.nodeType == Node.ELEMENT_NODE:
                    yield Row(row)
        return row_iter(self.data.childNodes)

    def name(self):
        return str(self.rows[0][0])

class Document(object):
    def __init__(self, data):
        self.doc = minidom.parseString('<doc>\n' + data + '</doc>\n')
        self.data = self.doc.childNodes[0]

    def html(self):
        html = ''
        for node in self.data.childNodes:
            html += node.toxml()
        return html

    def visit_tables(self, visitor):

        for node in self.data.childNodes:
            if node.nodeName == 'table':
                visitor.process(Table(node))

