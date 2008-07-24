import socket
import sys
from new import *

reply = '''<table border="1" cellspacing="0">
<tr><td colspan="2">CalculateDiscount</td>
</tr>
<tr><td><i>amount</i></td>
<td><i>discount()</i></td>
</tr>
<tr><td>0.00</td>
<td class="pass">0.00</td>
</tr>
<tr><td>100.00</td>
<td class="pass">0.00</td>
</tr>
<tr><td>999.00</td>
<td class="pass">0.00</td>
</tr>
<tr><td>1000.00</td>
<td class="fail">0.00 <span class="fit_label">expected</span><hr>50.0 <span class="fit_label">actual</span></td>
</tr>
<tr><td>1010.00</td>
<td class="pass">50.50</td>
</tr>
<tr><td>1100.00</td>
<td class="pass">55.00</td>
</tr>
<tr><td>1200.00</td>
<td class="pass">60.00</td>
</tr>
<tr><td>2000.00</td>
<td class="pass">100.00</td>
</tr>
</table>
'''

class FitServer(object):
    def __init__(self):
        self.host = sys.argv[2]
        self.port =  int(sys.argv[3])
        self.socketToken = sys.argv[4]
        print 'token: %s' % self.socketToken
        print 'host/port: %s:%s' % (self.host, self.port)
        
    def _makeHttpRequest(self):
        return ("GET /?responder=socketCatcher&ticket=%s HTTP/1.1\r\n\r\n"
                % self.socketToken)
    
    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        return None

    def writeSize(self, length):
        lengthBytes = "%010i" % length
        self.write(lengthBytes)

    def read_document(self):
        sizeString = self.read(10)
        print 'read bytes=[%s]' % sizeString
        document = ''
        if int(sizeString) > 0:
            document = self.read(int(sizeString))
        print 'document [%s]' % document
        return document

    def run(self):
        self.connect(self.host, self.port)
        request = self._makeHttpRequest()
        bytes = request.encode("UTF-8")
        self.write(bytes)
        sizeString = self.read(10)
        print sizeString
        document = self.read_document()
        sizeString = self.read(10)
        print sizeString

        table = Parse(document)
        table.format()
        
        name = table.name()
        engine = CreateFixtureEngine(name, table)
        engine.run()
        os = FakeFile()
        write_html(os, table)
        reply = os.data

        from xml.dom import minidom, Node

        print reply
        doc = minidom.parseString(reply)
        reply = doc.toxml()

        self.writeSize(len(reply))
        self.write(reply)

        self.write('0000000000')
        self.write('0000000007')
        self.write('0000000001')
        self.write('0000000000')
        self.write('0000000000')
        self.socket.close()

    def read(self, size):
        print 'read size=%s' % size
        resultString = ""
        while len(resultString) < size:
            result = self.socket.recv(size - len(resultString))
            resultString += result
        return resultString.decode("utf-8")
        
    def write(self, document):
        print 'write socket [%s]' % document
        self.socket.sendall(document)


if __name__ == '__main__':
    server = FitServer()
    server.run()

