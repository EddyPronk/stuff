from LineItems import *

class BuyActions(object):
	def __init__(self):	
		self.lineItems = LineItems()
		self.currentPrice = 0.0
	def price(self, currentPrice):
		self.currentPrice = float(currentPrice)
	def buy(self):
		self.lineItems.buyFor(self.currentPrice)
	def total(self):
		return self.lineItems.totalIs()
