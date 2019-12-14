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

@dataclass
class FlashSaleMultiItem:
    website_name: str
    sale_name: str
    products: list
    time_left: datetime.timedelta

    def __str__(self):
        string_representation = "{} @ {}\n".format(self.sale_name, self.website_name)
        for index, product in enumerate(self.products):
            string_representation += """Item #{}:
item name:\t{}
old price:\t{} PLN
new price:\t{} PLN
items sold:\t{}
items left:\t{}\n""".format(
            index + 1, product["item_name"], product["old_price"],
            product["new_price"], product["sold"], product["remaining"])
        string_representation += "time left: {}".format(self.time_left)
        return string_representation