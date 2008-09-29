import unittest
from client import Client
from util import *
from table import *
from engines import Engine
import sys

class FakeTransport(object):
    def loseConnection(self):
        pass
    def write(self, data):
        if False:
            sys.stdout.write(data)

class TestClient(unittest.TestCase):
    def setUp(self):
        #self.context = FakeContext()
        self.client = Client()
        self.client.transport = FakeTransport()
        self.tables = []
        self.client.engine.print_traceback=False

    def add_table(self, wiki):
        html = wiki_table_to_html(wiki)
        self.tables.append(html)

    def html(self):
        return '\n\n'.join(self.tables)

    def _test_single_page(self):
        
        self.add_table('|Table1|')
        self.add_table('|Table2|')

        self.client.content(self.html())
        #self.assertEqual(self.context.reports, 1)

    def test_multi_page(self):

        self.add_table('|Table1|')
        self.add_table('|Table2|')
        self.client.content(self.html())

        self.add_table('|Table3|')
        self.add_table('|Table4|')
        self.client.content(self.html())

        #self.assertEqual(self.context.reports, 2)
