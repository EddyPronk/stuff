import unittest
from ListExecutor import ListExecutor
from SlimError import SlimError

'''
package fitnesse.slim;

import fitnesse.slim.converters.VoidConverter;
import static fitnesse.util.ListUtility.list;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import org.junit.Before;
import org.junit.Test;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;


'''
import sys


EXCEPTION_TAG = '__EXCEPTION__:'

def resultToMap(slimResults):
    m = {}
    for aResult in slimResults:
        resultList = aResult
        m[resultList[0]] = resultList[1]
    return m

class ListExecutorTest(unittest.TestCase):

    def setUp(self):
        self.executor = ListExecutor()
        self.statements = []
        self.expectedResults = []
        self.statements.append(["i1", "import", "fitnesse.slim.test"])
        self.statements.append(["m1", "make", "testSlim", "TestSlim"])
        self.expectedResults.append(["i1", "OK"])
        self.expectedResults.append(["m1", "OK"])

    def respondsWith(self, expected):
        self.expectedResults.extend(expected)
        result = self.executor.execute(self.statements)
        expectedMap = resultToMap(self.expectedResults)
        resultMap = resultToMap(result)
        self.assertEquals(expectedMap, resultMap)

    def testInvalidOperation(self):
        self.statements.append(["inv1", "invalidOperation"])
        self.assertExceptionReturned("message:<<INVALID_STATEMENT: invalidOperation.>>", "inv1")

    def testMalformedStatement(self):
        self.statements.append(["id", "call", "notEnoughArguments"])
        self.assertRaises(SlimError, self.assertExceptionReturned, "XX", "id")

    def assertExceptionReturned(self, message, returnTag):
        results = resultToMap(self.executor.execute(self.statements))
        result = results[returnTag]
        self.assert_(result.find(EXCEPTION_TAG) != -1)
        self.assert_(result.find(message) != -1)

    def testNoSuchInstance(self):
        self.statements.append(["id", "call", "noSuchInstance", "noSuchMethod"])
        self.assertExceptionReturned("message:<<NO_INSTANCE noSuchInstance.>>", "id")

    def testEmptyListReturnsNicely(self):
        self.executor.execute(self.statements)
        self.respondsWith([])
    '''

  public void createWithFullyQualifiedNameWorks() throws Exception {
    statements.clear();
    statements.add(list("m1", "make", "testSlim", "fitnesse.slim.test.TestSlim"));
    expectedResults.clear();
    respondsWith(list(list("m1", "OK")));
  }

  '''
    def testOneFunctionCall(self):
        self.statements.append(["id", "call", "testSlim", "returnString"])
        self.respondsWith([["id", "string"]])

    def testCanPassArgumentsToConstructor(self):
        self.statements.append(["m2", "make", "testSlim2", "TestSlim", "3"])
        self.statements.append(["c1", "call", "testSlim2", "returnConstructorArg"])
        self.statements.append(["c2", "call", "testSlim", "returnConstructorArg"])
        self.respondsWith(
            [
                ["m2", "OK"],
                ["c1", "3"],
                ["c2", "0"]])

    def testMultiFunctionCall(self):
        self.statements.append(["id1", "call", "testSlim", "addTo", "1", "2"])
        self.statements.append(["id2", "call", "testSlim", "addTo", "3", "4"])
        self.respondsWith([["id1", "3"], ["id2", "7"]])

    def testCallAndAssign(self):
        self.statements.append(["id1", "callAndAssign", "v", "testSlim", "addTo", "5", "6"])
        self.statements.append(["id2", "call", "testSlim", "echoInt", "$v"])
        self.respondsWith([["id1", "11"], ["id2", "11"]])

    def testCanReplaceMultipleVariablesInAnArgument(self):
        self.statements.append(["id1", "callAndAssign", "v1", "testSlim", "echoString", "Bob"])
        self.statements.append(["id2", "callAndAssign", "v2", "testSlim", "echoString", "Martin"])
        self.statements.append(["id3", "call", "testSlim", "echoString", "name: $v1 $v2"])
        self.respondsWith([["id1", "Bob"], ["id2", "Martin"], ["id3", "name: Bob Martin"]])

    '''
  public void passAndReturnList() throws Exception {
    List<String> l = list("one", "two");
    statements.add(list("id", "call", "testSlim", "echoList", l));
    respondsWith(list(list("id", l)));
  }
'''
    def testPassAndReturnListWithVariable(self):
        self.statements.append(["id1", "callAndAssign", "v", "testSlim", "addTo", "3", "4"])
        self.statements.append(["id2", "call", "testSlim", "echoList", ["$v"]])
        self.respondsWith([["id1", "7"], ["id2", ["7"]]])

    def testCallToVoidFunctionReturnsVoidValue(self):
        self.statements.append(["id", "call", "testSlim", "voidFunction"])
        #self.respondsWith([["id", VoidConverter.VOID_TAG]])

    def testCallToFunctionReturningNull(self):
        self.statements.append(["id", "call", "testSlim", "nullString"])
        self.respondsWith([["id", None]])

if __name__ == '__main__':
    import sys
    sys.path.append('/home/epronk/stuff/pyfit')
    unittest.main()

