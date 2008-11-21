from Statement import Statement
from StatementExecutor import StatementExecutor

'''
package fitnesse.slim;

import java.util.ArrayList;
import java.util.List;

import fitnesse.util.ListUtility;
'''

'''
 executes a list of SLIM statements, and returns a list of return values.
'''

class ListExecutor(object):

    def __init__(self, verbose = False):
        self.verbose = verbose
        self.executor = StatementExecutor()

    '''
  private StatementExecutor executor;
  private boolean verbose;

  public ListExecutor() {
    this(false);
  }

  public ListExecutor(boolean verbose) {
    this.verbose = verbose;
    this.executor = new StatementExecutor();
  }

'''
    def execute(self, statements):
        message = "!1 Instructions"
        self.verboseMessage(message)

        result = []
        for statement in statements:
            statementList = statement
            self.verboseMessage(str(statementList) + "\n")
            retVal = Statement(statementList).execute(self.executor)
            self.verboseMessage(retVal)
            self.verboseMessage("------");
            result.append(retVal)
        return result

    def verboseMessage(self, message):
        if self.verbose:
            System.out.println(message)
