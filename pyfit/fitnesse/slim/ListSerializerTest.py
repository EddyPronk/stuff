import unittest
import ListSerializer
    
class ListSerializerTest(unittest.TestCase):

    def setUp(self):
        self.data = []

    def testNullListSerialize(self):
        self.assertEquals("[000000:]", ListSerializer.serialize(self.data))

    def testOneItemListSerialize(self):
        self.data.append("hello")
        self.assertEquals("[000001:000005:hello:]", ListSerializer.serialize(self.data))

    def testTwoItemListSerialize(self):
        self.data.append("hello")
        self.data.append("world")
        self.assertEquals("[000002:000005:hello:000005:world:]", ListSerializer.serialize(self.data))

    def testSerializeNestedList(self):
        sublist = []
        sublist.append("element")
        self.data.append(sublist)
        self.assertEquals("[000001:000024:[000001:000007:element:]:]", ListSerializer.serialize(self.data))

    def testSerializeListWithNonString(self):
        s = ListSerializer.serialize([ 1 ])
        #data = ListDeserializer.deserialize(s)
        #assertEquals("1", list.get(0))

    def testSerializeNullElement(self):
        data = [ None ]
        s = ListSerializer.serialize(data);
        self.assertEquals("[000001:000004:null:]", s)

if __name__ == '__main__':
    unittest.main()
