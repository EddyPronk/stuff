import traceback
from util import *

class DefaultLoader(object):
    def load(self, name):
        try:
            module = self.do_load(name)
        except ImportError, inst:
            a = traceback.format_exc()
            print '{\n%s}' % inst.value
        names = name.split('.')[1:]
        for name in names:
            module = getattr(module, name)
        class_ = getattr(module, name)
        return class_()

    def do_load(self, name):
        return __import__(name)

class StringLoader(DefaultLoader):
    def __init__(self, script):
        self.script = script
    def do_load(self, name):
        x = compile(self.script, 'not_a_file.py', 'exec')
        eval(x)
            
class Engine(object):
    
    # return the next object in the flow or None.
    # check if fixture has attribute with name of next table.
    # if not create an instance with that name
    def __init__(self):
        self.loader = DefaultLoader()
        self.fixture = None
        self.print_traceback = False
        self.adapters = DefaultAdapters()

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

        self.fixture.adapters = self.adapters

    def do_process(self, table):
        name = table.name()
        self.load_fixture(name)
        self.fixture.process(table)

    def process(self, table, throw = True):
        name = table.name()
        
        if throw == True:
            self.do_process(table)
        else:
            try:
                self.do_process(table)
            except Exception, inst:
                '''Fixme: Should the rest of the table become grey?'''

                print inst

                #table.cell(0,0).error(inst)
                if self.print_traceback:
                    print 'Processing table `%s` failed' % table.name()
                    print '====='
                    print traceback.format_exc()
                    print '====='
        
        return self.fixture

