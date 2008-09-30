from xml.dom import minidom, Node
import workaround

def create_table(node):
    rows = []
    for row in node.childNodes:
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
        self.doc = data.ownerDocument
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

    def tag(self, text):
        node = self.doc.createElement("span")
        node.appendChild(self.doc.createTextNode(text))
        node.setAttribute("class", "fit_label")
        return node

    def failed(self, actual_value):
        self.data.setAttribute("class", "fail")
        expected_value = self.data.childNodes[0].nodeValue
        doc = self.data.ownerDocument
        expected = self.tag("expected")
        actual = self.tag("actual")
        hr = doc.createElement("hr")
        hr.appendChild(doc.createTextNode(str(expected_value) + ' '))
        self.data.replaceChild(hr, self.data.childNodes[0])
        value = doc.createTextNode(str(actual_value) + ' ')
        self.data.insertBefore(expected, self.data.childNodes[0])
        self.data.insertBefore(value, self.data.childNodes[0])
        self.data.appendChild(actual)

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
        tag = self.tag(text)
        self.data.appendChild(tag)

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
        return cell

class Row(object):
    def __init__(self, data):
        self.data = data

    def __iter__(self):
        return RowDomIter(self.data.childNodes[0])

class Table(object):
    def __init__(self, data):
        if type(data) is str:
            #self.doc = minidom.parseString(data)
            self.doc = workaround.parse_xml(data)
            #print type(self.doc)
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

    def append_row(self, row):
        doc = self.data.ownerDocument
        tr = doc.createElement("tr")
        for cell in row:
            td = doc.createElement("td")
            td.appendChild(doc.createTextNode(cell))
            tr.appendChild(td)
        self.data.appendChild(tr)
        Cell(tr.childNodes[0]).surplus()
    
    def toxml(self):
        return self.data.toxml()

class Document(object):
    def __init__(self, data):
        xml = '<doc>\n' + data + '</doc>\n'
        #self.doc = minidom.parseString(xml)
        self.doc = workaround.parse_xml(xml)
        self.data = self.doc.childNodes[0]

    def html(self):
        html = ''
        for node in self.data.childNodes:
            html += node.toxml()
        return html

    def visit_tables(self, visitor):

        def visit(tree, visitor):
            for node in tree.childNodes:
                if node.nodeName == 'table':
                    visitor.on_table(Table(node))
                else:
                    visit(node, visitor)
        visit(self.data, visitor)
        visitor.report()

