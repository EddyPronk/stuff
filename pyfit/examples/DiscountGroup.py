class DiscountGroup(object):
    def __init__(self, futureValue, maxOwing, 
                 minPurchase, discountPercent):
        self.future_value = futureValue
        self.max_owing = maxOwing
        self.min_purchase = minPurchase
        self.discount_percent = discountPercent
        self.description = ""

def getElements():
    return [
        DiscountGroup("low",      0.0,    0.0,  0.0),
        DiscountGroup("low",      0.0, 2000.0,  3.0),
        DiscountGroup("medium", 500.0,  600.0,  3.0),
        DiscountGroup("medium",   0.0,  500.0,  5.0),
        DiscountGroup("high",  2000.0, 2000.0, 10.0)
       ]
