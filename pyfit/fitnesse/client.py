from twisted.internet.protocol import Protocol, ClientFactory, Factory
import util
import sys

class Client(Protocol):
    def __init__(self, context):
        self.context = context
        self.state = 0
        #self.data = ''

    def connectionMade(self):
        self.socketToken = sys.argv[4]
        print 'connection made'
        request = "GET /?responder=socketCatcher&ticket=%s HTTP/1.1\r\n\r\n" % self.socketToken
        bytes = request.encode("UTF-8")
        self.transport.write(bytes)
        #d.addAddcallback(self.dataReceived)

        #self.transport.loseConnection()

    def dataReceived(self, data):
        print 'client data received'
        print '[%s]' % data

        file = util.FileAdapter()
        file.data += data
        while file.data is not '':
            if self.state is 0:
                print 'state 0'
                length = int(file.read(10))
                if length is 0:
                    print 'received ack'
                    self.state = 0
                else:
                    self.state = 1
            elif self.state is 1:
                self.state = 0
                print 'state 1'
                content = file.read(length)
                output = self.context.process(content)
        #reactor.stop()
                self.transport.write(util.format_10_digit_number(len(output) + 1))
                print 'sending content back'
                self.transport.write(output)
                self.transport.write('\n')
                self.transport.write(util.format_10_digit_number(0))
                self.transport.write(util.format_10_digit_number(0))
                self.transport.write(util.format_10_digit_number(0))
                self.transport.write(util.format_10_digit_number(0))
                self.transport.write(util.format_10_digit_number(0))
                self.transport.loseConnection()
