from Credit import Credit
from ColumnFixture import ColumnFixture

class CalculateCredit(ColumnFixture):
    months = 0
    reliable = False
    balance = 0.0
    credit = Credit()

    def allow_credit(self):
        return self.credit.allowsCredit(self.months, self.reliable, self.balance)

    def credit_limit(self):
        return self.credit.limit(self.months, self.reliable, self.balance)

    
