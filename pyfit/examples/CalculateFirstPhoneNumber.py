from Client import Client
from fit.ColumnFixture import ColumnFixture

class CalculateFirstPhoneNumber(ColumnFixture):
    client = Client()
    phones = []
    def first(self):
        self.client.setPhones(self.phones)
        return self.client.firstPhone()
