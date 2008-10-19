class Credit(object):

    def allowsCredit(self, months, reliable, balance):
        return months > 12 and reliable and balance < 6000

    def limit(self, months, reliable, balance):
        if self.allowsCredit(months, reliable, balance):
            return 1000.0
        else:
            return 0.0
