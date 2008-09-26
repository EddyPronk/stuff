#from table import *
from fixtures import *

#from table import *
import traceback

class Engine(object):
    
    # return the next object in the flow or None.
    # check if fixture has attribute with name of next table.
    # if not create an instance with that name
    def __init__(self):
        def DefaultFixtureFactory(name):
            try:
                module = __import__(name)
            except Exception, e:
                a = traceback.format_exc()
                print '{\n%s}' % str(a)
            class_ = getattr(module, name)
            return class_()

        self.FixtureFactory = DefaultFixtureFactory
        self.fixture = None

    def process(self, table):
        name = table.name()
        if self.fixture is None:
            self.fixture = self.FixtureFactory(name)
        else:
            try:
                f = getattr(self.fixture, name)
                self.fixture = f()
            except AttributeError, inst:
                self.fixture = self.FixtureFactory(name)
        
        if self.fixture is None:
            raise Exception("fixture '%s' not found." % name)

        self.fixture.process(table)
        
        def do_process(self,table):
            try:
                self.fixture.process(table)
            except Exception, inst:
                '''Fixme: Should the rest of the table become grey?'''
                table.cell(0,0).error(inst)

        return self.fixture

class Context(object):
    def process(self, content):
        print 'content : [%s]' % content
        engine = Engine()
        doc = Document(content)
        doc.visit_tables(engine)
        return str(doc.html())

