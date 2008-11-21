from SlimError import SlimError

'''
 Specifies the syntactic operations for a Slim statement.  A Slim statement is a list of strings.
 The first string is the operation name.  Other strings are arguments of the operation.  This class knows
 that syntax, and knows how to decompose it into StatementExecutor calls.  This class DOES NOT know how
 to do any actual execution.  
'''

class Statement(object):
    def __init__(self, statement):
        self.words = statement

    '''
  private ArrayList<Object> words = new ArrayList<Object>();

  public Statement(List<Object> statement) {
    for (Object word : statement)
      words.add(word);
  }

  public boolean add(Object s) {
    return words.add(s);
  }

  public boolean addAll(Collection<Object> objects) {
    return words.addAll(objects);
  }
'''
    def operationIs(self, operation):
        return self.getOperation() == operation

    def getOperation(self):
        return self.getWord(1)

    def getWord(self, word):
        try:
            return self.words[word]
        except Exception, e:
            raise SlimError('message:<<MALFORMED_INSTRUCTION %s.>>' % self.toString())

    def toString(self):
        result = '['
        for word in self.words:
            result += word
            result += ','
        if result[-1] == ',' :
            result = result[:-1]
        result += ']'
        return result

    def execute(self, executor):
        if (self.operationIs("make")):
            retval =  self.createInstance(executor);
        elif (self.operationIs("import")):
            retval =  self.addPath(executor)
        elif (self.operationIs("call")):
            retval =  self.call(executor);
        elif (self.operationIs("callAndAssign")):
            retval =  self.callAndAssign(executor);
        else:
            retval = '__EXCEPTION__:'  +  'message:<<INVALID_STATEMENT: %s.>>' % self.getOperation()
        return [ self.getWord(0), retval ]

    def addPath(self, caller):
        return caller.addPath(self.getWord(2))

    def createInstance(self, caller):
        instanceName = self.getWord(2)
        className = self.getWord(3)
        args = self.makeArgsArray(4)
        return caller.create(instanceName, className, args)

    def call(self, caller):
        return self.callMethodAtIndex(caller, 2)

    def callMethodAtIndex(self, caller, methodIndex):
        instanceName = self.getWord(methodIndex + 0)
        methodName = self.getWord(methodIndex + 1)
        args = self.makeArgsArray(methodIndex + 2)
        return caller.call(instanceName, methodName, args)

    def makeArgsArray(self, argsIndex):
        argList = self.words[argsIndex:]
        args = argList
        return args

    def callAndAssign(self, caller):
        result = self.callMethodAtIndex(caller, 3)
        caller.setVariable(self.getWord(2), result)
        return result
