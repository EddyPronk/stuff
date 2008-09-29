from twisted.internet.protocol import Protocol, ClientFactory, Factory
from protocol import Protocol as FitnesseProtocol
import util
import sys
from table import *
from engines import Engine

class Client(Protocol):
    def __init__(self):
        self.engine = Engine()
        self.logfile = open('logfile', 'w')
        self.proto = FitnesseProtocol(self)
        self.output_pages = []

    def ack(self):
        self.ack_received = True

    def connectionMade(self):
        self.socketToken = sys.argv[4]
        print 'connection made'
        request = "GET /?responder=socketCatcher&ticket=%s HTTP/1.1\r\n\r\n" % self.socketToken
        bytes = request.encode("UTF-8")
        self.transport.write(bytes)
        #d.addAddcallback(self.dataReceived)

        #self.transport.loseConnection()

    def dataReceived(self, data):
        self.logfile.write('dataReceived [%s]\n' % data)
        print 'client data received'
        print '[%s]' % data
        self.proto.dataReceived(data)

    def content(self, data):
        doc = Document(data)
        doc.visit_tables(self)

    def on_table(self, table):
        fixture = self.engine.process(table, throw=False)
        self.write_table(table)
    
    def done(self):
        self.transport.loseConnection()
        
    def write_table(self, table):
        html = str(table.toxml()) # Fixme : str() workaround for 'Data must not be unicode'
        self.transport.write(util.format_10_digit_number(len(html) + 1))
        self.transport.write(html)
        self.transport.write('\n')
        
    def report(self):
        #self.transport.write('report\n')
        # 0 right, 0 wrong, 0 ignored, 0 exceptions
        self.transport.write(util.format_10_digit_number(0))
        self.transport.write(util.format_10_digit_number(1))
        self.transport.write(util.format_10_digit_number(2))
        self.transport.write(util.format_10_digit_number(3))
        self.transport.write(util.format_10_digit_number(4))
