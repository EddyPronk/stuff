from SlimError import SlimError
from engines import DefaultLoader
import re

#from util import *

EXCEPTION_TAG = '__EXCEPTION__:'

'''
package fitnesse.slim;

import fitnesse.slim.converters.*;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.lang.reflect.Constructor;
import java.lang.reflect.Method;
import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
'''

'''
 This is the API for executing a SLIM statement.  This class should not know about
 the syntax of a SLIM statement.
'''

class StatementExecutor(object):

    def __init__(self):
        self.instances = {}
        self.variables = {}
        self.paths = []

        #Slim.addConverter(void.class, new VoidConverter())
        #Slim.addConverter(String.class, new StringConverter())
        #Slim.addConverter(int.class, new IntConverter())
        #Slim.addConverter(double.class, new DoubleConverter())
        #Slim.addConverter(Integer.class, new IntConverter())
        #Slim.addConverter(Double.class, new DoubleConverter())
        #Slim.addConverter(char.class, new CharConverter())
        #Slim.addConverter(boolean.class, new BooleanConverter())
        #Slim.addConverter(Boolean.class, new BooleanConverter())
        #Slim.addConverter(Date.class, new DateConverter())
        #Slim.addConverter(List.class, new ListConverter())
        #Slim.addConverter(Integer[].class, new IntegerArrayConverter())
        #Slim.addConverter(int[].class, new IntegerArrayConverter())
        #Slim.addConverter(String[].class, new StringArrayConverter())
        #Slim.addConverter(boolean[].class, new BooleanArrayConverter())
        #Slim.addConverter(Boolean[].class, new BooleanArrayConverter())
        #Slim.addConverter(double[].class, new DoubleArrayConverter())
        #Slim.addConverter(Double[].class, new DoubleArrayConverter())

    def setVariable(self, name, value):
        self.variables[name] = value

    def addPath(self, path):
        self.paths.append(path)
        return "OK"

    def getInstance(self, instanceName):
        instance = self.instances.get(instanceName)
        if (instance != None):
            return instance
        raise SlimError('message:<<NO_INSTANCE %s.>>' % instanceName)

    def getConverter(self, k):
        return Slim.converters.get(k)

    def create(self, instanceName, className, args):
        try:
            instance = self.createInstanceOfConstructor(className, args) # self.replaceVariables(args))
            self.instances[instanceName] = instance
            return "OK";
        except Exception, e:
            print e
            return self.exceptionToString(
                SlimError(
                    'message:<<COULD_NOT_INVOKE_CONSTRUCTOR %s[%d]>>' % (className, len(args))))

    def createInstanceOfConstructor(self, className, args):
        k = self.searchPathsForClass(className);
        #constructor = self.getConstructor(k.getConstructors(), args);
        #if constructor == None:
        #    raise SlimError('message:<<NO_CONSTRUCTOR %s>>' % className)
        return k(*args) #constructor.newInstance(convertArgs(args, constructor.getParameterTypes()))

    def searchPathsForClass(self, className):
        k = self.getClass(className)
        if k != None:
            return k
        for path in self.paths:

            k = self.getClass(path + "." + className);
            if k != None:
                return k
        raise SlimError('message:<<NO_CLASS %s>>' % className)

    def getClass(self, className):
        try:
            t = DefaultLoader().load(className)
            return t
        except Exception, e:
            return None # ???

    '''
  private Constructor<?> getConstructor(Constructor<?>[] constructors, Object[] args) {
    for (Constructor<?> constructor : constructors) {
      Class<?> arguments[] = constructor.getParameterTypes();
      if (arguments.length == args.length)
        return constructor;
    }
    return null;
  }
'''

    def call(self, instanceName, methodName, args):
        try:
            instance = self.getInstance(instanceName)
            return self.tryToInvokeMethod(instance, methodName, self.replaceVariables(args))
        except Exception, e:
            return self.exceptionToString(e)

    def exceptionToString(self, e):
        return EXCEPTION_TAG + str(e)

    def replaceVariables(self, args):
        result = []
        for arg in args:
            result.append(self.replaceVariable(arg))
        return result

    def replaceArgsInList(self, objects):
        result = []
        for object in objects:
            result.append(self.replaceVariable(object))
        return result

    def replaceVariable(self, object):
        if type(object) is list:
            return self.replaceArgsInList(object)
        else:
            return self.replaceVariablesInString(object)

    def replaceVariablesInString(self, arg):
        symbolPattern = re.compile("\\$([a-zA-Z]\\w*)");
        startingPosition = 0
        while True:
            symbolMatcher = symbolPattern.search(arg[startingPosition:])
            if symbolMatcher is not None:
                symbolName = symbolMatcher.group(1)
                if self.variables.has_key(symbolName):
                    arg = arg.replace("$" + symbolName, self.variables.get(symbolName))
                startingPosition += symbolMatcher.start(1)
            else:
                break
        return arg

    def tryToInvokeMethod(self, instance, methodName, args):
        method =  getattr(instance, methodName)
        return method(*args)

'''
  private Method findMatchingMethod(String methodName, Class<? extends Object> k, int nArgs) {
    Method methods[] = k.getMethods();

    for (Method method : methods) {
      boolean hasMatchingName = method.getName().equals(methodName);
      boolean hasMatchingArguments = method.getParameterTypes().length == nArgs;
      if (hasMatchingName && hasMatchingArguments)
        return method;
    }
    throw new SlimError(String.format("message:<<NO_METHOD_IN_CLASS %s[%d] %s.>>", methodName, nArgs, k.getName()));
  }

  private Object[] convertArgs(Method method, Object args[]) {
    Class<?>[] argumentTypes = method.getParameterTypes();
    Object[] convertedArgs = convertArgs(args, argumentTypes);
    return convertedArgs;
  }

  //todo refactor this mess
  private Object[] convertArgs(Object[] args, Class<?>[] argumentTypes) {
    Object[] convertedArgs = new Object[args.length];
    for (int i = 0; i < argumentTypes.length; i++) {
      Class<?> argumentType = argumentTypes[i];
      if (argumentType == List.class && args[i] instanceof List) {
        convertedArgs[i] = args[i];
      } else {
        Converter converter = getConverter(argumentType);
        if (converter != null)
          convertedArgs[i] = converter.fromString((String) args[i]);
        else
          throw
            new SlimError(String.format("message:<<NO_CONVERTER_FOR_ARGUMENT_NUMBER %s.>>", argumentType.getName()));
      }
    }
    return convertedArgs;
  }

  private Object convertToString(Object retval, Class<?> retType) {
    Converter converter = getConverter(retType);
    if (converter != null)
      return converter.toString(retval);
    if (retval == null)
      return "null";
    else
      return retval.toString();
  }
}
'''
