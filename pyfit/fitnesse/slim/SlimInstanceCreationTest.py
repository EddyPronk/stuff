import unittest
from StatementExecutor import StatementExecutor
from fitnesse.slim.test.TestSlim import TestSlim
import SlimServer

'''package fitnesse.slim;

import fitnesse.slim.test.TestSlim;
import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import org.junit.Before;
import org.junit.Test;

'''
class SlimInstanceCreationTest(unittest.TestCase):

    def setUp(self):
        self.caller = StatementExecutor()

    def testCanCreateInstance(self):
        response = self.caller.create("x", "fitnesse.slim.test.TestSlim", []);
        self.assertEquals("OK", response);
        x = self.caller.getInstance("x");
        self.assertEquals(type(x), TestSlim)

    def testCanCreateInstanceWithArguments(self):
        response = self.caller.create("x", "fitnesse.slim.test.TestSlim", [3]);
        self.assertEquals("OK", response);
        x = self.caller.getInstance("x");
        self.assertEquals(x.constructorArg, 3)
        self.assertEquals(type(x), TestSlim)

    def testCantCreateInstanceIfConstructorArgumentBad(self):
        result = self.caller.create("x", "fitnesse.slim.test.TestSlim", [ "notInt" ])
        #self.assertException("message:<<COULD_NOT_INVOKE_CONSTRUCTOR fitnesse.slim.test.TestSlim[1]>>", result)


    def testCantCreateInstanceIfConstructorArgumentCountIncorrect(self):
        result = self.caller.create("x", "fitnesse.slim.test.TestSlim", ["3","4"])
        self.assertException("message:<<COULD_NOT_INVOKE_CONSTRUCTOR fitnesse.slim.test.TestSlim[2]>>", result)

    def testThrowsInstanceNotCreatedErrorIfNoSuchClass(self):
        result = self.caller.create("x", "fitnesse.slim.test.NoSuchClass", [])
        self.assertException("message:<<COULD_NOT_INVOKE_CONSTRUCTOR fitnesse.slim.test.NoSuchClass[0]>>", result)

    def testThrowsInstanceNotCreatedErrorIfNoPublicDefaultConstructor(self):
        result = self.caller.create("x", "fitnesse.slim.test.ClassWithNoPublicDefaultConstructor", [])
        self.assertException("message:<<COULD_NOT_INVOKE_CONSTRUCTOR fitnesse.slim.test.ClassWithNoPublicDefaultConstructor[0]>>", result);

    def assertException(self, message, result):
        self.assert_(result.find(SlimServer.EXCEPTION_TAG) != -1)
        self.assert_(result.find(message) != -1)

if __name__ == '__main__':
    unittest.main()
