from table import *
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

class Context(object):
    def process(self, content):
        print 'content : [%s]' % content

        doc = Document(content)
        doc.visit_tables()
        return str(doc.html())

