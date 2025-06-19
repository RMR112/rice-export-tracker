class Order:
    def __init__(self, buyer, country, variety, quantity_mt, price_per_mt, order_date, expected_ship_date, notes=""):
        self.buyer = buyer
        self.country = country
        self.variety = variety
        self.quantity_mt = quantity_mt
        self.price_per_mt = price_per_mt
        self.order_date = order_date
        self.expected_ship_date = expected_ship_date
        self.notes = notes


