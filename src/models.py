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


class Shipment:
    def __init__(self, container_id, vessel_name, departure_date, status, notes=""):
        self.container_id = container_id
        self.vessel_name = vessel_name
        self.departure_date = departure_date
        self.status = status
        self.notes = notes