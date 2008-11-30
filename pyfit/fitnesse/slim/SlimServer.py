from twisted.internet.protocol import Protocol, ClientFactory, Factory
#from protocol import Protocol as FitnesseProtocol
import util
import sys

EXCEPTION_TAG = "__EXCEPTION__:"

class SlimServer(Protocol):
    def __init__(self):
        pass

    def connectionMade(self):
        print 'connectionMade'

    def dataReceived(self, data):
        print 'dataReceived ', data

