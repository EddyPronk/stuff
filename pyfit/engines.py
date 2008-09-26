import traceback
from util import *

class DefaultLoader(object):
    def load(name):
        try:
            module = __import__(name)
        except ImportError, inst:
            a = traceback.format_exc()
            print '{\n%s}' % inst.value
        class_ = getattr(module, name)
        return class_()

class Engine(object):
    
    # return the next object in the flow or None.
    # check if fixture has attribute with name of next table.
    # if not create an instance with that name
    def __init__(self):
        self.loader = DefaultLoader()
        self.fixture = None

    def load_fixture(self, name):
        if self.fixture is None:
            self.fixture = self.loader.load(name)
        else:
            try:
                f = getattr(self.fixture, name)
                self.fixture = f()
            except AttributeError, inst:
                self.fixture = self.loader.load(name)
        
        if self.fixture is None:
            raise Exception("fixture '%s' not found." % name)

    def process(self, table):
        name = table.name()
        self.load_fixture(name)
        self.fixture.process(table)
        
        def do_process(self,table):
            try:
                self.fixture.process(table)
            except Exception, inst:
                '''Fixme: Should the rest of the table become grey?'''
                table.cell(0,0).error(inst)

        return self.fixture

