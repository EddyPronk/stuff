from LineItems import *
from fit.ColumnFixture import ColumnFixture

class BuyActionsWithColumn(ColumnFixture):
    def __init__(self):
        self.lineItems = LineItems()
        self.price = 0.0
    def total(self):
        self.lineItems.buyFor(self.price)
        return self.lineItems.totalIs()
