import unittest
import ListSerializer
import ListDeserializer
from ListDeserializer import deserialize
from ListDeserializer import SlimSyntaxError

class ListDeserializerTest(unittest.TestCase):

    def setUp(self):
        self.data = []
        
    def check(self):
        serialized = ListSerializer.serialize(self.data)
        deserialized = deserialize(serialized)
        self.assertEquals(self.data, deserialized)

    def testCantDeseriailzeNullString(self):
        self.assertRaises(SlimSyntaxError, ListDeserializer.deserialize, None)

    def testCantDeserializeEmptyString(self):
        self.assertRaises(SlimSyntaxError, ListDeserializer.deserialize, '')

    def testCantDeserializeStringThatDoesntStartWithBracket(self):
        self.assertRaises(SlimSyntaxError, ListDeserializer.deserialize, 'hello')

    def testCantDeserializeStringThatDoesntEndWithBracket(self):
        self.assertRaises(SlimSyntaxError, ListDeserializer.deserialize, '[000000:')

    def testEmptyList(self):
        self.check()

    def testListWithOneElement(self):
        self.data.append("hello")
        self.check()

    def testListWithTwoElements(self):
        self.data.append("hello")
        self.data.append("world")
        self.check()

    def testListWithSubList(self):
        sublist = []
        sublist.append("hello");
        sublist.append("world");
        self.data.append(sublist);
        self.data.append("single");
        self.check();

if __name__ == '__main__':
    unittest.main()
