# 20080316 2h
# 20080317 3h

import copy
import unittest

class Order :
    def __init__(self, side, code, price, quantity):
        self.side = side
        self.price = price
        self.quantity = quantity

class Trade :
    def __init__(self):
        pass

class OrderQueue :
    def __init__(self):
        self.levels = {}
        self.orders = {}
        self.subscribers = []

    def add(self, order, id):
        order.id = id
        self.orders[id] = copy.copy(order)
        #self.orders[id] = order
        if self.levels.has_key(order.price):
            level = self.levels[order.price]
        else:
            level = Level()
            self.levels[order.price] = level

            for subscriber in self.subscribers:
                subscriber.on_price_level_added(order.price)

        level.orders.append(order)
        #self.sell_queue.add(order)

    def amend(self, order):
        old_order = self.orders[order.id]
        level = self.levels[old_order.price]
        if order.price != old_order.price:
            for xorder in level.orders:
                if xorder.id == order.id:
                    xorder.price = order.price
                    level.orders.remove(xorder)
                    if len(level.orders) == 0:
                        del self.levels[old_order.price]
                        for subscriber in self.subscribers:
                            subscriber.on_price_level_removed(order.price)
                    self.add(xorder, order.id)

    def remove(self, price, id):
        level = self.levels[price]
        for order in level.orders:
            if order.id == id:
                level.orders.remove(order)

        if len(level.orders) == 0:
            del self.levels[price]
            for subscriber in self.subscribers:
                subscriber.on_price_level_removed(order.price)

class BuyOrderQueue(OrderQueue) :
    def best_price(self):
        return self.levels.keys()[-1]
    def best_price_level(self):
        return self.levels[self.best_price()]

class SellOrderQueue(OrderQueue) :
    def best_price(self):
        return self.levels.keys()[0]
    def best_price_level(self):
        return self.levels[self.best_price()]

class Level :
    def __init__(self):
        self.orders = []

def sell_order(code="BHP", price=50, quantity=100):
    return Order('Sell', code, price, quantity)

def buy_order(code="BHP", price=50, quantity=100):
    return Order('Buy', code, price, quantity)
    
class Market :
    def __init__(self):
        self.order_id = 0
        self.sell_queue = SellOrderQueue()
        self.buy_queue = BuyOrderQueue()
        self.trade_subscribers = []
        self.order_subscribers = []

    def place_order(self, order):
        self.order_id += 1
        #for subscriber in self.order_subscribers:
        #    subscriber.on_order_added(order)
        if order.side == 'Buy':
            self.buy_queue.add(order, self.order_id)
        else:
            self.sell_queue.add(order, self.order_id)
        self.match()
        return self.order_id

    def new_buy_order(self, order):
        self.order_id += 1
        for subscriber in self.order_subscribers:
            subscriber.on_order_added(order)
        self.buy_queue.add(order, self.order_id)
        self.match()
        return self.order_id

    def amend_order(self, order):
        if order.side == 'Buy':
            self.buy_queue.amend(order)
        else:
            self.sell_queue.amend(order)
        self.match()

    def reduce(self, queue, order, quantity):
        order.quantity -= quantity
        if order.quantity == 0:
            for subscriber in self.order_subscribers:
                subscriber.on_order_removed(order)
            queue.remove(order.price, order.id)
        else:
            for subscriber in self.order_subscribers:
                subscriber.on_order_changed(order)

    def dump(self):
        print 'market:'
        print 'sell:'
        if self.sell_queue.levels:
            print 'best price = %s' % self.sell_queue.best_price()
        for level, v in self.sell_queue.levels.iteritems():
            print 'level %s' % level
            for i in v.orders:
                print i.__dict__
        print 'buy:'
        if self.buy_queue.levels:
            print 'best price = %s' % self.buy_queue.best_price()
        for level,v in self.buy_queue.levels.iteritems():
            print 'level %s' % level
            for i in v.orders:
                print i.__dict__


    def match(self):
        if self.buy_queue.levels and self.sell_queue.levels:
            trade = Trade()
            buy_order = self.buy_queue.best_price_level().orders[0]
            sell_order = self.sell_queue.best_price_level().orders[0]
            quantity=  min(sell_order.quantity, buy_order.quantity)
            if buy_order.price >= sell_order.price:
                self.reduce(self.buy_queue, buy_order, quantity)
                self.reduce(self.sell_queue, sell_order, quantity)
                for subscriber in self.trade_subscribers:
                    subscriber.on_trade(trade)
                self.match()

class Exchange :
    def __init__(self):
        self.market = Market()

    def login(self):
        return self

    def place_order(self, order):
        return self.market.place_order(order)

    def amend_order(self, order):
        return self.market.amend_order(order)


class Trades:
    def __init__(self):
        self.trades = []

    def on_trade(self, trade):
        self.trades.append(trade)

class Orders:
    def __init__(self):
        self.orders = []

    def on_order_added(self, order):
        print 'order added', order.__dict__

    def on_order_changed(self, order):
        print 'order changed', order.__dict__

    def on_order_removed(self, order):
        print 'order removed', order.__dict__

class Prices:
    def __init__(self):
        pass

    def on_price_level_added(self, price):
        print 'price level added : %s' % price

class TestOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = BuyOrderQueue()
        self.queue.subscribers.append(self)

    def on_price_level_added(self, price) : pass
    def on_price_level_removed(self, price) : pass

    def testBest(self):
        order = buy_order(code='BHP', price=49, quantity=10)
        order.id = 5
        self.queue.add(order, order.id)
        self.queue.remove(order.price, 5)

class TestBidOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = BuyOrderQueue()
        #self.queue.subscribers.append(self)

    def on_price_level_added(self, price):
        print price

    def testBest(self):
        order_id1 = self.queue.add(sell_order(price=49, quantity=10), id=1)
        order_id1 = self.queue.add(sell_order(price=49, quantity=10), id=2)
        self.assertEqual(self.queue.best_price(), 49)

class TestOfferOrderQueue(unittest.TestCase):
    def setUp(self):
        self.queue = SellOrderQueue()
        #self.queue.subscribers.append(self)

    def on_price_level_added(self, price):
        print price

    def testBest(self):
        order_id1 = self.queue.add(buy_order(price=52, quantity=10), id=1)
        order_id1 = self.queue.add(buy_order(price=51, quantity=10), id=2)
        self.assertEqual(self.queue.best_price(), 51)

class TestMarket(unittest.TestCase):
    
    def setUp(self):
        self.asx = Exchange()
        self.connection = self.asx.login()
        self.trades = Trades()
        self.orders = Orders()

        self.prices = Prices()
        #self.asx.market.price_subscribers.append(self.prices)
        #self.asx.market.order_subscribers.append(self.orders)
        self.asx.market.trade_subscribers.append(self.trades)

    def testNoMatch(self):
        order_id1 = self.connection.place_order(sell_order(price=50, quantity=10))
        order_id2 = self.connection.place_order(buy_order(price=49, quantity=5))
        self.assertEqual(len(self.trades.trades), 0)

    def testMatch(self):
        order_id1 = self.connection.place_order(sell_order(price=50, quantity=10))
        order_id2 = self.connection.place_order(buy_order(price=50, quantity=5))
        self.assertEqual(len(self.trades.trades), 1)
        self.assertEqual(len(self.connection.market.buy_queue.levels), 0)
        self.assertEqual(len(self.connection.market.sell_queue.levels), 1)

    def testMatch2(self):
        order_id1 = self.connection.place_order(sell_order(price=50, quantity=5))
        order_id2 = self.connection.place_order(sell_order(price=50, quantity=5))
        order_id3 = self.connection.place_order(buy_order(price=50, quantity=10))
        self.assertEqual(len(self.trades.trades), 2)

    def testTickUp(self):
        order_id1 = self.connection.place_order(sell_order( price=50, quantity=10))
        buy_order1 = buy_order( price=49, quantity=5)
        order_id2 = self.connection.place_order(buy_order1)
        self.assertEqual(len(self.trades.trades), 0)
        buy_order1.price=50
        self.connection.amend_order(buy_order1)
        self.assertEqual(len(self.trades.trades), 1)
        #self.connection.market.dump()
        
        #self.assertEqual(len(self.connection.market.buy_queue.levels), 0)
        #self.assertEqual(len(self.connection.market.sell_queue.levels), 1)

    def testTickUp2(self):
        self.connection.place_order(sell_order(price=50, quantity=10))
        self.connection.place_order(buy_order(price=49, quantity=10))
        buy_order1 = buy_order(price=49, quantity=15)
        order_id2 = self.connection.place_order(buy_order1)
        self.assertEqual(len(self.trades.trades), 0)
        buy_order1.price=50
        self.connection.amend_order(buy_order1)
        self.assertEqual(len(self.trades.trades), 1)
        #self.connection.market.dump()

if __name__ == '__main__':
    unittest.main()
