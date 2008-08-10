import sys
from twisted.internet.protocol import Protocol, ClientFactory, Factory
from twisted.internet import reactor
from fitnesse.client import Client
from context import Context
import util

class FitnesseClientFactory(ClientFactory):
    def startedConnecting(self, connector):
        print 'Started to connect.'
    
    def buildProtocol(self, addr):
        self.context = Context()
        self.protocol = Client(self.context)
        return self.protocol
    
    def clientConnectionLost(self, connector, reason):
        #print 'Lost connection.  Reason:', reason
        reactor.stop()
    
    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason

host = sys.argv[2]
port =  int(sys.argv[3])
socketToken = sys.argv[4]

client_factory = FitnesseClientFactory()
reactor.connectTCP(host, port, client_factory)
reactor.run()
