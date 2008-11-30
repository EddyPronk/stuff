import traceback
from twisted.internet.protocol import Protocol, ClientFactory, Factory
from twisted.internet import reactor
import ListSerializer
import ListDeserializer
from ListExecutor import ListExecutor
###from twisted.internet import reactor
#from protocol import Protocol as FitnesseProtocol
import sys
logfile = open('log', 'w')
sys.path.append('/home/epronk/stuff/pyfit')

def log(entry):
    #print entry
    logfile.write(entry)
    logfile.flush()

class FileAdapter(object):
    def __init__(self, data):
        self.data = data
        self.offset = 0
    def read(self, n):
        end = self.offset + n
        block = self.data[self.offset:end]
        self.offset = end
        return block
    def eof(self):
        return self.offset >= len(self.data)

class SlimServer(Protocol):
    def __init__(self):
        log('init')

    def connectionMade(self):
        log('connectionMade')
        self.transport.write("Slim -- V0.0\n");

    def dataReceived(self, data):
        #log('dataReceived ' + data)
        try:
            self.file = FileAdapter(data)
            instructionLength = int(self.file.read(6))
            self.file.read(1)
            instructions = self.file.read(instructionLength)
            if instructions == 'bye':
                #self.transport.loseConnection()
                reactor.stop()
                return
            log('instructions {%s}' % instructions)
            statements = ListDeserializer.deserialize(instructions)
            self.executor = ListExecutor()
            results = self.executor.execute(statements)
            x = ListSerializer.serialize(results)
            log(x)
            self.transport.write('%06d:%s' % (len(x), x))
        except Exception, e:
            log(traceback.format_exc())
        #results = executor.execute(statements)
        #self.transport.write(data)

try:
    import sys
    #from fitnesse.client import Client
    #import util


    log('args : %s' % sys.argv)
    path = sys.argv[1]
    #util.add_to_python_path(path)
    #host = sys.argv[2]
    host = 'localhost'
    port =  int(sys.argv[3]) # was 3
    #socketToken = sys.argv[4]
    
    factory = Factory()
    factory.protocol = SlimServer

    print port
    reactor.listenTCP(port, factory)
    reactor.run()
    log('done')

except Exception, e:
    log(traceback.format_exc())

