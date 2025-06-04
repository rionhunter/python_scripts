# models.py

class StockItem:
    def __init__(self, name, availability, condition, price):
        self.name = name
        self.availability = availability
        self.condition = condition
        self.price = price

    def update_availability(self, availability):
        self.availability = availability

    def update_condition(self, condition):
        self.condition = condition

    def update_price(self, price):
        self.price = price


class StockDatabase:
    def __init__(self):
        self.stock_items = []

    def add_stock_item(self, stock_item):
        self.stock_items.append(stock_item)

    def search_stock_item(self, name):
        for item in self.stock_items:
            if item.name == name:
                return item
        return None

    def update_stock_item(self, item_name, availability=None, condition=None, price=None):
        item = self.search_stock_item(item_name)
        if item:
            if availability is not None:
                item.update_availability(availability)
            if condition is not None:
                item.update_condition(condition)
            if price is not None:
                item.update_price(price)

    def generate_stock_report(self):
        report = []
        for item in self.stock_items:
            report.append(f"Item: {item.name}, Availability: {item.availability}, Condition: {item.condition}, Price: {item.price}")
        return report

# Changes Made:
# 1. Made sure the update_stock_item method checks for None explicitly in the if conditions for availability, condition, and price.
# 2. This change ensures that the update_stock_item method can handle cases where the availability/condition/price can be 0 or False.
# 3. This change improves the durability and allows for more precise updates to StockItem attributes.
# 4. No other changes were required to ensure cohesion, ease of testing, and debugging.