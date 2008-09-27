from table import *
from fixtures import *
from engines import Engine

#from table import *
import traceback

class Context(object):
    def process(self, content):
        print 'content : [%s]' % content
        engine = Engine()
        doc = Document(content)
        doc.visit_tables(engine)
        return str(doc.html())

