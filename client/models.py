from django.db import models


# Create your models here.
class MenuItem(object):
    def __init__(self, receiver_name, receiver_address, receiver_contact, pickup_time, payable_amt, ordered_items):
        self.receiver_name = receiver_name
        self.receiver_address = receiver_address
        self.receiver_contact = receiver_contact
        self.pickup_time = pickup_time
        self.payable_amt = payable_amt
        self.ordered_items = ordered_items

    def serialize(self):
        return self.__dict__


class MenuItem1(object):

    def __init__(self,distinct_order_keys, product, product_varient, quantity, addons, addons_quantity, date_delivery, time, message, pound, \
                 is_eggless, is_sugarless, shipping_method,key=""):
        self.distinct_order_keys=distinct_order_keys
        self.product = product
        self.product_varient = product_varient
        self.quantity = quantity
        self.addons = addons
        self.addons_quantity = addons_quantity
        self.date_delivery = date_delivery
        self.time = time
        self.message = message
        self.pound = pound
        self.is_eggless = is_eggless
        self.is_sugarless = is_sugarless
        self.shipping_method = shipping_method
        self.key = key
        

    def serialize(self):
        return self.__dict__
