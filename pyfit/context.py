#from table import *
from fixtures import *


output = '<span class="meta">variable defined: COMMAND_PATTERN=python2.5 %m %p</span><br/><span class="meta">variable defined: TEST_RUNNER=/home/epronk/PyFIT.git/fit/FitServer.py</span><br/><br/><table border="1" cellspacing="0">\n' \
    '<tr><td colspan="2">CalculateDiscount</td>\n' \
    '</tr>\n' \
    '<tr><td><i>amount</i></td>\n' \
    '<td><i>discount()</i></td>\n' \
    '</tr>\n' \
    '<tr><td>0.00</td>\n' \
    '<td class="pass">0.00</td>\n' \
    '</tr>\n' \
    '<tr><td>100.00</td>\n' \
    '<td class="pass">0.00</td>\n' \
    '</tr>\n' \
    '<tr><td>999.00</td>\n' \
    '<td class="pass">0.00</td>\n' \
    '</tr>\n' \
    '<tr><td>1000.00</td>\n' \
    '<td class="fail">0.00 <span class="fit_label">expected</span><hr>50.0 <span class="fit_label">actual</span></td>\n' \
    '</tr>\n' \
    '<tr><td>1010.00</td>\n' \
    '<td class="pass">50.50</td>\n' \
    '</tr>\n' \
    '<tr><td>1100.00</td>\n' \
    '<td class="pass">55.00</td>\n' \
    '</tr>\n' \
    '<tr><td>1200.00</td>\n' \
    '<td class="pass">60.00</td>\n' \
    '</tr>\n' \
    '<tr><td>2000.00</td>\n' \
    '<td class="pass">100.00</td>\n' \
    '</tr>\n' \
    '</table>\n'

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

        return self.fixture

class Context(object):
    def process(self, content):
        print 'content : [%s]' % content
        engine = Engine()
        doc = Document(content)
        doc.visit_tables(engine)
        return str(doc.html())

