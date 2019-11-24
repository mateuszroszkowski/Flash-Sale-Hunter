from dataclasses import dataclass
import datetime

@dataclass
class FlashSale:
    website_name: str
    sale_name: str
    item_name: str
    old_price: str
    new_price: str
    items_sold: str
    items_left: str
    time_left: datetime.timedelta

    def __str__(self):
        return """{} @ {}
item name:\t{}
old price:\t{} PLN
new price:\t{} PLN
items sold:\t{}
items left:\t{}
time left:\t{}""".format(
            self.sale_name, self.website_name, self.item_name,
            self.old_price, self.new_price, self.items_sold,
            self.items_left, self.time_left)