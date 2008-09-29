from util import FileAdapter

class Protocol(object):
    def __init__(self, client):
        self.client = client
        self.process = self.process_func()
    
    def dataReceived(self, data):
        self.file = FileAdapter(data)
        while self.file.eof():
            self.process.next()

    def read_length(self):
        return int(self.file.read(10))

    def process_func(self):
        length = self.read_length()
        if length is 0:
            self.client.ack()
            yield

        while True:
            length = self.read_length()
            if length is 0:
                self.client.done()
                yield
            else:
                yield
                content = self.file.read(length)
                self.client.content(content)
                yield
