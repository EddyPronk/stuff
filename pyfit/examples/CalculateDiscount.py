from fit.ColumnFixture import ColumnFixture

class CalculateDiscount(ColumnFixture):

    amount = 0.0

    def discount(self):
        if (self.amount < 0):
            raise Exception("Can't be a negative amount")
        if (self.amount < 1000):
            return 0.0
        else:
            return self.amount*0.05;
