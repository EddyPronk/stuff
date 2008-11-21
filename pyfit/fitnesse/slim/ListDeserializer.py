def deserialize(serialized):
    return ListDeserializer(serialized).deserialize();

'''
 Uses Slim Serialization.  See ListSerializer for details.  Will deserialize lists of lists recursively.
'''

class ListDeserializer(object):
    def __init__(self, serialized):
        self.serialized = serialized
        self.result = []
        self.index = 0

    def deserialize(self):
        try:
            self.checkSerializedStringIsValid()
            return self.deserializeString()
        except Exception, e:
            raise SlimSyntaxError(e)

    def checkSerializedStringIsValid(self):
        if self.serialized == None:
            raise SlimSyntaxError("Can't deserialize null")
        elif len(self.serialized) == 0:
            raise SlimSyntaxError("Can't deserialize empty string")

    def deserializeString(self):
        self.checkForOpenBracket()
        result = self.deserializeList()
        self.checkForClosedBracket()
        return result
    
    def checkForClosedBracket(self):
        if (not self.charsLeft() or self.getChar() != ']'):
            raise SlimSyntaxError("Serialized list has no ending ]");

    def charsLeft(self):
        return self.index < len(self.serialized)

    def checkForOpenBracket(self):
        if self.getChar() != '[':
            raise SlimSyntaxError("Serialized list has no starting [")

    def deserializeList(self):

        itemCount = self.getLength()
        for i in range(0, itemCount):
            self.deserializeItem()
        
        return self.result

    def deserializeItem(self):
        itemLength = self.getLength()
        item = self.getString(itemLength)
        try:
            sublist = deserialize(item)
            self.result.append(sublist)
        except SlimSyntaxError, e:
            self.result.append(item)

    def getString(self, length):
        result = self.serialized[self.index:self.index + length]
        self.index += length
        self.checkForColon("String")
        return result

    def checkForColon(self, itemType):
        if self.getChar() != ':':
            raise SlimSyntaxError(itemType + " in serialized list not terminated by colon.")

    def getChar(self):
        c = self.serialized[self.index]
        self.index += 1
        return c

    def getLength(self):
        return self.tryGetLength()
        try:
            return self.tryGetLength()
        except NumberFormatException, e:
            raise SyntaxError(e)

    def tryGetLength(self):
        lengthSize = 6
        lengthString = self.serialized[self.index:self.index + lengthSize]
        length = int(lengthString)
        self.index += lengthSize;
        self.checkForColon("Length")
        return length

class SlimSyntaxError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

