class LineItems(object):
    total = 0.0

    def buyFor(self, price):
        self.total += price

    def totalIs(self):
        return self.total
