import unittest
from protocol import Protocol

class TestProtocol(unittest.TestCase):
    def setUp(self):
        self.proto = Protocol(self)
        self.pages = 0
    
    def ack(self):
        self.ack_received = True

    def content(self, content):
        self.pages += 1

    def done(self):
        self.done_received = True

    def test_ack(self):
        self.proto.dataReceived('0000000000')
        self.assert_(self.ack_received)

    def test_length_and_content_in_seperate_blocks(self):
        self.proto.dataReceived('0000000000')
        self.proto.dataReceived('0000000004')
        self.proto.dataReceived('abcd')
        self.proto.dataReceived('0000000000')
        self.assertEqual(self.pages, 1)
        self.assert_(self.done_received)

    def test_length_and_content_in_same_block(self):
        self.proto.dataReceived('0000000000')
        self.proto.dataReceived('0000000004abcd')
        self.proto.dataReceived('0000000000')
        self.assertEqual(self.pages, 1)
        self.assert_(self.done_received)

    def test_suite_of_2_pages(self):
        self.proto.dataReceived('0000000000')
        self.proto.dataReceived('0000000004')
        self.proto.dataReceived('abcd')
        self.proto.dataReceived('0000000004')
        self.proto.dataReceived('abcd')
        self.proto.dataReceived('0000000000')
        self.assertEqual(self.pages, 2)
        self.assert_(self.done_received)
