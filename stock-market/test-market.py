# 20080316 2h
# 20080317 3h
# 20080317 1h

import copy
import unittest
import string

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

class LevelSummary :
    def __init__(self):
        self.sell_quantity = 0
        self.buy_quantity = 0

class OrderIdAllocator:
    def __init__(self):
        self.order_id = 0

    def allocate(self, order):
        self.order_id += 1
        return self.order_id

class Market :
    def __init__(self):
        self.state = 'Open'
        self.code = 'BHP'
        self.levels = {}
        self.order_id_allocator = OrderIdAllocator()
        self.sell_queue = SellOrderQueue()
        self.buy_queue = BuyOrderQueue()
        self.trade_subscribers = []
        self.order_subscribers = []

    def place_order(self, order):
        if order.quantity == 0:
            return
        order_id = self.order_id_allocator.allocate(order)
        #for subscriber in self.order_subscribers:
        #    subscriber.on_order_added(order)

        if self.levels.has_key(order.price):
            level = self.levels[order.price]
        else:
            level = LevelSummary()
            self.levels[order.price] = level

        if order.side == 'Buy':
            self.buy_queue.add(order, order_id)
            level.buy_quantity += order.quantity
        else:
            self.sell_queue.add(order, order_id)
            level.sell_quantity += order.quantity
        self.match()
        return order_id

    def set_state(self, state):
        self.state = state
        self.match()

    def cancel_order(self, order):
        pass

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

    def printLevels(self):
        print
        x = self.levels.keys()
        x.reverse()
        for p in x:
            l = self.levels[p]
            print "%5i %5i %5i" % (l.buy_quantity, p, l.sell_quantity)

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
        if self.state != 'Open' : return
        if self.buy_queue.levels and self.sell_queue.levels:
            buy_order = self.buy_queue.best_price_level().orders[0]
            sell_order = self.sell_queue.best_price_level().orders[0]
            quantity=  min(sell_order.quantity, buy_order.quantity)
            if buy_order.price >= sell_order.price:
                trade = Trade()
                trade.code = self.code
                trade.quantity = quantity
                trade.price = sell_order.price
                trade.sell_order_id = sell_order.id
                trade.buy_order_id = buy_order.id
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

    def cancel_order(self, order):
        return self.market.cancel_order(order)

########################################################
# TEST CODE

def sell_order(code="BHP", price=50, quantity=100):
    return Order('Sell', code, price, quantity)

def buy_order(code="BHP", price=50, quantity=100):
    return Order('Buy', code, price, quantity)
    
class Trades:
    def __init__(self):
        self.trades = []

    def on_trade(self, trade):
        self.trades.append(trade)
        #print trade.__dict__

class Orders:
    def __init__(self):
        self.orders = []

    def on_order_added(self, order):
        print 'order added', order.__dict__

    def on_order_changed(self, order):
        print 'order changed', order.__dict__

    def on_order_removed(self, order):
        print 'order removed', order.__dict__

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

        #self.asx.market.price_subscribers.append(self.prices)
        #self.asx.market.order_subscribers.append(self.orders)
        self.asx.market.trade_subscribers.append(self.trades)

    def testCancel(self):
        order_id1 = self.connection.place_order(sell_order(price=50, quantity=10))
        self.connection.cancel_order(order_id1)

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

    def testOpeningRotation(self):
        market = self.connection.market
        market.set_state('Closed')
        order_id1 = self.connection.place_order(sell_order(price=50, quantity=5))
        order_id2 = self.connection.place_order(sell_order(price=50, quantity=5))
        order_id3 = self.connection.place_order(buy_order(price=50, quantity=5))
        order_id3 = self.connection.place_order(buy_order(price=50, quantity=5))
        self.assertEqual(len(self.trades.trades), 0)
        market.set_state('Open')
        self.assertEqual(len(self.trades.trades), 2)

    def testIterate(self):
        market = self.connection.market
        market.set_state('Closed')

        x = '''\
            4500 825  8500
           28200 824 16900
               0 823  1900
            1900 822     0
               0 821     0
           49700 820 17500
            8000 819  3600
           16400 818 11600'''

        for line in x.split('\n'):
            q1, p, q2 = [string.atoi(v) for v in line.split()]
            self.connection.place_order(buy_order(price=p, quantity=q1))
            self.connection.place_order(sell_order(price=p, quantity=q2))

        self.connection.market.printLevels()

def levelIter(l1, l2):
    it1 = iter(l1)
    it2 = iter(l2)
    v = None
    try:
        v = it1.next()
    except StopIteration:
        pass

    if v == None:
        try:
            v = it2.next()
        except StopIteration:
            yield None

    yield v

    prev = 0
    while(v != None):
        v = None
        try:
            v = it1.next()
        except StopIteration:
            pass

        if v == None:
            try:
                v = it2.next()
            except StopIteration:
                yield None

        if v > prev:
            prev = v
            yield v

class TestIter(unittest.TestCase):
    def setUp(self):
        pass

    def testBothEmpty(self):
        x = levelIter([],[])
        self.assertEqual(None, x.next())

    def testSecondEmpty(self):
        x = levelIter([1],[])
        self.assertEqual(1, x.next())

    def testSecondEmpty2(self):
        x = levelIter([2],[])
        self.assertEqual(2, x.next())

    def testFirstEmpty(self):
        x = levelIter([],[1])
        self.assertEqual(1, x.next())

    def testFirstEmpty(self):
        x = levelIter([1,2],[])
        self.assertEqual(1, x.next())
        self.assertEqual(2, x.next())

    def testFirstEmpty25(self):
        x = levelIter([],[2])
        self.assertEqual(2, x.next())
        self.assertEqual(None, x.next())

    def testFirstEmpty(self):
        x = levelIter([1],[2])
        self.assertEqual(1, x.next())
        self.assertEqual(2, x.next())

    def testFirstEmpty2(self):
        x = levelIter([1,2],[3])
        self.assertEqual(1, x.next())
        self.assertEqual(2, x.next())
        self.assertEqual(3, x.next())

    def testFirstEmpty3(self):
        x = levelIter([1],[2,3])
        self.assertEqual(1, x.next())
        self.assertEqual(2, x.next())
        self.assertEqual(3, x.next())

    def testFirstEmpty3(self):
        x = levelIter([1,2],[2,3])
        self.assertEqual(1, x.next())
        self.assertEqual(2, x.next())
        self.assertEqual(3, x.next())
        
if __name__ == '__main__':
    unittest.main()
