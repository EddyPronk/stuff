from fit.RowFixture import RowFixture
import DiscountGroup

class DiscountGroupOrderedList(RowFixture):
    def query(self):
        elements =  DiscountGroup.getElements()
        for (i, item) in enumerate(elements):
            item.order = str(i + 1)
        return elements
