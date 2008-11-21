class TestSlim(object):
    
    def __init__(self, constructorArg = '0'):
        self.constructorArg = constructorArg

    def returnString(self):
        return "string"

    def returnConstructorArg(self):
        return self.constructorArg

    def addTo(self, a, b):
        return str(int(a) + int(b))

    def echoInt(self, i):
        return i

    def echoString(self, s):
        return s

    def echoList(self, l):
        return l

    def nullString(self):
        return None

