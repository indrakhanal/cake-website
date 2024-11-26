from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator, MinValueValidator
from datetime import datetime, timedelta
import secrets
from settings.models import *
from django.contrib.postgres.fields import JSONField
from catalog.models import ProductVarient, Product, ProductAddons
from marketing.models import CartCoupon
from settings.models import ShippingMethod
from django.forms.models import model_to_dict
from django.db.models import Q
from django.db.models import Sum
from store.models import Factories



class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    coupon = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Carts'
        ordering = ('-id',)

    def __str__(self):
        return self.user.username

    def discounted_total(self):
        if self.coupon:
            return self.get_sub_total()+self.get_shipping_price_total()-self.discount
        else:
            return self.get_sub_total()+self.get_shipping_price_total()

    def discounted_sub_total(self):
        if self.coupon:
            return self.get_sub_total()-self.discount
        else:
            return self.get_sub_total()

    # def total(self):
    #     return self.get_sub_total()

    def get_sub_total(self):
        sub_total = 0
        for item in self.items.all():
            sub_total += item.get_sub_total()
        return sub_total

    def get_total_with_shipping_method(self):
        return self.get_sub_total()+self.get_shipping_price_total()

    def get_shipping_price_total(self):
      total = 0
      for item in self.items.all():
        total += (item.shipping_method.price*item.quantity)
      return total

    def get_addon_total(self):
        addon_total = 0
        for item in self.items.all():
            addon_total += item.addonTotal
        return addon_total

    def cart_count(self):
        count = 0
        for item in self.items.all():
            count = count+item.quantity
        return count

    @property
    def is_unique_item_only(self):
        return self.items.all().count()

    @property
    def cart_list(self):
        items = self.items.all()
        cart_list = []
        for i in items:
            varient = ProductVarient.objects.filter(id=i.product_id)
            cart_list.append({'varient': varient, 'display_price': i.display_price,
                              'base_product': i.product.product.name, 'quantity': i.quantity, 'varient_count': i.product.product.varientCount(),
                              'message': i.message, 'pound': i.pound, 'eggless': i.is_eggless, 'sugarless': i.is_sugarless,
                              'eggless_price': i.eggless_price*i.quantity,
                              'sugarless_price': i.sugarless_price*i.quantity,
                              'display_price_with_egg_sugar_and_addon': i.display_price_with_egg_sugar_and_addon,
                              'date': i.date,
                              'time': i.time,
                              'delivery_time':i.delivery__time,
                              'addon_total_price': i.addonTotal})
        return cart_list

    @property
    def cart_list_jsonResponse(self):
        items = self.items.all()
        cart_list = []
        for i in items:
            FIELDS = {'id', 'varient_name', 'slug', 'product',
                      'old_price', 'price', 'product_code', 'quantity'}
            varient = model_to_dict(ProductVarient.objects.get(
                id=i.product.id), fields=FIELDS)
            cart_list.append({'varient': varient, 'display_price': i.display_price,
                              'base_product': i.product.product.name, 'quantity': i.quantity,
                              'message': i.message, 'pound': i.pound, 'eggless': i.is_eggless, 'sugarless': i.is_sugarless,
                              'eggless_price': i.eggless_price,
                              'sugarless_price': i.sugarless_price,
                              'display_price_with_egg_sugar_and_addon': i.display_price_with_egg_sugar_and_addon,
                              'date': i.date,
                              'time': i.time,
                              'addon_total_price': i.addonTotal})
        return cart_list

    @property
    def discount(self):
        if self.coupon:
            coupon = get_object_or_404(CartCoupon, coupon_number=self.coupon)
            if coupon.coupon_type == 'Flat':
                discount = coupon.value
                return discount
            if coupon.coupon_type == 'Percentage':
                discount = (coupon.value/100)*self.get_sub_total()
                return discount
        else:
            return 0

    """Return sum of varient quantity in cart and add 1 to it.  """
    @classmethod
    def total_quantity_varient(cls,varient,user):
        quantity=0
        item=CartItem.objects.filter(cart__user=user,product=varient)
        for i in item:
            quantity=quantity+i.quantity
        return quantity+1

    
import pdb

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items',
                             on_delete=models.CASCADE, blank=False)
    product = models.ForeignKey(
        ProductVarient, related_name='cart_items', on_delete=models.CASCADE)
    quantity = models.IntegerField(
        default=1, validators=[MinValueValidator(1)])
    date = models.CharField(max_length=20)
    time = models.CharField(max_length=20)
    message = models.TextField(max_length=40, blank=True, null=True)
    shipping_method = models.ForeignKey(
        ShippingMethod, related_name='item_shipping_method', on_delete=models.CASCADE)
    is_eggless = models.BooleanField(default=False)
    is_sugarless = models.BooleanField(default=False)
    pound = models.FloatField()
    photo_cake_image = models.ImageField(
        upload_to='cart/photocake/', blank=True, null=True, max_length=700)

    class Meta:
        ordering = ('-id',)
        verbose_name_plural = 'Cart Items'

    def get_sub_total(self):
        return self.product.selling_price*self.quantity+self.addonTotal+self.eggSugarLessTotal.get('egg_sugar_less_total')*self.quantity

    def get_total_with_shipping_cost(self):
      return self.get_sub_total()+(self.shipping_method.price* self.quantity)
      
    @property
    def display_price(self):
        return int(self.product.selling_price)*int(self.quantity)

    @property
    def addonTotal(self):
        total = 0
        for i in self.item_addons.all():
            total = total+i.total()
        return total

    @property
    def display_price_with_egg_sugar_and_addon(self):
        egg_sugar_less_total = self.eggSugarLessTotal.get(
            'egg_sugar_less_total')
        display_price_with_egg_sugar_and_addon = self.product.selling_price * \
            self.quantity+egg_sugar_less_total*self.quantity+self.addonTotal
        return display_price_with_egg_sugar_and_addon

    @property
    def eggless_price(self):
        return self.eggSugarLessTotal.get('eggless_price')

    @property
    def sugarless_price(self):
        return self.eggSugarLessTotal.get('sugarless_price')

    @property
    def eggSugarLessTotal(self):
        store = self.product.product.store
        if store.flat_eggless:
            if self.is_eggless and self.is_sugarless:
                egg_sugar_less_total = store.sugar_less_price+store.eggless_price
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price, 'sugarless_price': store.sugar_less_price}
            if self.is_eggless and not self.is_sugarless:
                egg_sugar_less_total = store.eggless_price
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price, 'sugarless_price': 0}
            if self.is_sugarless and not self.is_eggless:
                egg_sugar_less_total = store.sugar_less_price
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': 0, 'sugarless_price': store.sugar_less_price}
            else:
                return {'egg_sugar_less_total': 0, 'eggless_price': 0, 'sugarless_price': 0}
        else:
            if self.is_eggless and self.is_sugarless:
                egg_sugar_less_total = store.sugar_less_price + \
                    (store.eggless_price*self.pound)
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price*self.pound, 'sugarless_price': store.sugar_less_price}
            if self.is_eggless and not self.is_sugarless:
                egg_sugar_less_total = store.eggless_price*self.pound
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price*self.pound, 'sugarless_price': 0}
            if self.is_sugarless and not self.is_eggless:
                egg_sugar_less_total = store.sugar_less_price
                return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': 0, 'sugarless_price': store.sugar_less_price}
            else:
                return {'egg_sugar_less_total': 0, 'eggless_price': 0, 'sugarless_price': 0}

    @classmethod
    def addToCart(cls, cart, varient, date_delivery, time, is_eggless, is_sugarless, message, shipping_method, pound, quantity, addons, addons_quantity, url_for_photo_cake):
        if cls.objects.filter(cart=cart, product=varient, date=date_delivery, time=time):
            item = cls.objects.get(cart=cart, product=varient,
                                   date=date_delivery, time=time)
            quantity = item.quantity+int(quantity)
            cls.objects.filter(cart=cart, product=varient,
                               date=date_delivery, time=time).update(quantity=quantity)
            item = cls.objects.get(cart=cart, product=varient,
                                   date=date_delivery, time=time)
            a = 0
            if addons and len(addons) >= 1:
                for i in addons:
                    addon = get_object_or_404(ProductAddons, id=i)
                    if AddonItem.objects.filter(cart_item=item, addons=addon):
                        itemAddon = get_object_or_404(
                            AddonItem, cart_item=item, addons=addon)
                        addon_quantity = itemAddon.quantity + \
                            int(addons_quantity[a])
                        AddonItem.objects.filter(cart_item=item, addons=addon).update(
                            quantity=addon_quantity)
                    else:
                        AddonItem.objects.create(
                            cart_item=item, addons=addon, quantity=addons_quantity[a])

                    a = a+1
        else:
            if is_eggless == 'yes':
                is_eggless = True
            else:
                is_eggless = False
            if is_sugarless == 'yes':
                is_sugarless = True
            else:
                is_sugarless = False
            
            try:
                pound = float(pound)
            except:
                pound = 0
            
            item = CartItem.objects.create(cart=cart, product=varient, quantity=quantity, date=date_delivery, time=time, message=message,
                                           shipping_method=shipping_method, is_eggless=is_eggless, is_sugarless=is_sugarless,
                                           pound=pound, photo_cake_image=url_for_photo_cake)
            a = 0
            if addons and len(addons) >= 1:
                for i in addons:
                    addon = get_object_or_404(ProductAddons, id=i)
                    AddonItem.objects.create(
                        cart_item=item, addons=addon, quantity=addons_quantity[a])
                    a = a+1

    @classmethod
    def apiaddToCart(cls, cart, varient, date_delivery, time, is_eggless, is_sugarless, message, shipping_method, pound, quantity, addons, url_for_photo_cake):
        if cls.objects.filter(cart=cart, product=varient, date=date_delivery, time=time):
            item = cls.objects.get(cart=cart, product=varient,
                                   date=date_delivery, time=time)
            quantity = item.quantity+int(quantity)
            cls.objects.filter(cart=cart, product=varient,
                               date=date_delivery, time=time).update(quantity=quantity)
            item = cls.objects.get(cart=cart, product=varient,
                                   date=date_delivery, time=time)
            if addons and len(addons) >= 1:
                for i in addons:
                    addon = get_object_or_404(ProductAddons, id=i["id"])
                    if AddonItem.objects.filter(cart_item=item, addons=addon):
                        itemAddon = get_object_or_404(
                            AddonItem, cart_item=item, addons=addon)
                        addon_quantity = itemAddon.quantity + \
                            int(i["addons_quantity"])
                        AddonItem.objects.filter(cart_item=item, addons=addon).update(
                            quantity=addon_quantity)
                    else:
                        AddonItem.objects.create(
                            cart_item=item, addons=addon, quantity=i["addons_quantity"])

        else:
            if is_eggless == 'yes':
                is_eggless = True
            else:
                is_eggless = False
            if is_sugarless == 'yes':
                is_sugarless = True
            else:
                is_sugarless = False
            
            try:
                pound = float(pound)
            except:
                pound = 0
            
            item = CartItem.objects.create(cart=cart, product=varient, quantity=quantity, date=date_delivery, time=time, message=message,
                                           shipping_method=shipping_method, is_eggless=is_eggless, is_sugarless=is_sugarless,
                                           pound=pound, photo_cake_image=url_for_photo_cake)
            # items_obj=get_object_or_404(CartItem,id=item)
            # item.photo_cake_image=str(url_for_photo_cake)
            # item.save()
            if addons and len(addons) >= 1:
                for i in addons:
                    addon = get_object_or_404(ProductAddons, id=i["id"])
                    AddonItem.objects.create(
                        cart_item=item, addons=addon, quantity=i["addons_quantity"])
    
    @property
    def delivery__time(self):
        from settings.models import ShippingTime
        time= ShippingTime.objects.get(id=self.time)
        return time
    

    """Placing Items as order as vender are differnet and date time is different"""
    @classmethod
    def possible_orders(cls,item):
        possible_orders=cls.objects.filter(cart=item.cart,date=item.date,time=item.time,product__product__store__name=item.product.product.store.name)
        return possible_orders

    """Return  total of items of same vendor place in same date and time"""
    @property
    def discounted_total_(self):
        return self.discounted_sub_total_+self.total_shipping_cost_
    
    """Return sub total of items of same vendor place in same date and time"""
    @property
    def discounted_sub_total_(self):
        total=0
        for i in CartItem.possible_orders(self):
            total =total+ i.product.selling_price*i.quantity+i.addonTotal+i.eggSugarLessTotal.get('egg_sugar_less_total')*self.quantity
        total=total-self.cart.discount
        return total
    
    """Return total shipping cost of possible unique order"""
    @property
    def total_shipping_cost_(self):
        total_shipping_cost=0
        for i in CartItem.possible_orders(self):
            total_shipping_cost=total_shipping_cost+(i.shipping_method.price*i.quantity)
        return total_shipping_cost
    
    

   
    
class AddonItem(models.Model):
    cart_item = models.ForeignKey(
        CartItem, related_name='item_addons', on_delete=models.CASCADE)
    addons = models.ForeignKey(
        ProductAddons, related_name='cart_addons', null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def total(self):
        return self.quantity*self.addons.price


class DeliveryAddress(models.Model):
    ADDRESS_TYPE = (('Home', 'Home'), ('Office', 'Office'), ('Other', 'Other'))
    OCCASION_TYPE = (('BIRTHDAY', 'Birthday'), ('ANNIVERSARY', 'Anniversary'),
                     ('BABY SHOWER', 'Baby Shower'), ('WEEDING', 'Weeding'))
    source_option = (('Instagram', 'Instagram'),
        ('Facebook', 'Facebook'),
        ('Phone', 'Phone'),
        ('WhatsApp', 'WhatsApp'),
        ('Bakery Order', 'Bakery Order'),
        ('Oho Staffs', 'Oho Staffs'),
        ('Other', 'Other'))
    CAKE_TYPE = (('Basic Fondent', 'Basic Fondent'),
        ('Fondent Cake', 'Fondent Cake'),
        ('Mini Cake', 'Mini Cake'),
        ('Normal Cake', 'Normal Cake'),
        )
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE, blank=True)
    receiver_fullname = models.CharField(max_length=30)
    receiver_email = models.EmailField(max_length=30)
    receiver_delivery_address = models.CharField(max_length=50)
    receiver_landmark = models.CharField(max_length=250, null=True, blank=True)
    receiver_city=models.CharField(max_length=250,null=True,blank=True)
    receiver_area=models.CharField(max_length=250,null=True,blank=True)
    receiver_address_type = models.CharField(
        max_length=15, choices=ADDRESS_TYPE)
    receiver_contact_number1 = models.CharField(
        max_length=20, validators=[RegexValidator(r'^\d{1,20}$')])
    receiver_contact_number2 = models.CharField(
        max_length=20, validators=[RegexValidator(r'^\d{1,20}$')],blank=True,null=True)
    occasion = models.CharField(max_length=15, choices=OCCASION_TYPE,blank=True,null=True)
    type_of_cake = models.CharField(max_length=15, choices=CAKE_TYPE,null=True)

    sender_fullname = models.CharField(max_length=30)
    sender_email = models.EmailField(blank=0, null=True)
    sender_address=models.CharField(max_length=100)
    social_media_handler = models.CharField(max_length = 250, null = True, blank = True)
    source = models.CharField(max_length=30,choices = source_option, default='Other')
    contact_number = models.CharField(max_length=20, validators=[
                                      RegexValidator(r'^\d{1,20}$')])
    hide_info_from_receiver = models.BooleanField(default=False)
    i_am_receiver = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Delivery Address'
        ordering = ('-id',)

    def __str__(self):
        return '{0}'.format(self.sender_fullname)

    def pickup_date_time(self):
        return self.pickup_time + timedelta(hours=5.75)

    @classmethod
    def createDeliveryAddress(cls, customer,i_am_receiver, receiver_fullname, receiver_email, receiver_address, landmark, address_type, receiver_number1, receiver_number2, occasion, sender_full_name, sender_phone_number, sender_email, hide_info_from_receiver,sender_address,city,area):
        from store.models import Location as StoreLocation
        obj = cls.objects.create(customer=customer,
            i_am_receiver=i_am_receiver,
                                 receiver_fullname=receiver_fullname,
                                 receiver_email=receiver_email,
                                 receiver_delivery_address=receiver_address,
                                 receiver_landmark=landmark,
                                 receiver_address_type=address_type,
                                 receiver_city=get_object_or_404(StoreLocation,id=city).name,
                                 receiver_area=get_object_or_404(StoreLocation,id=area).name,
                                 receiver_contact_number1=receiver_number1,
                                 receiver_contact_number2=receiver_number2,
                                 occasion=occasion,
                                 sender_fullname=sender_full_name,
                                 contact_number=sender_phone_number,
                                 sender_email=sender_email,
                                 sender_address=sender_address,
                                 hide_info_from_receiver=hide_info_from_receiver,
                                 )
        return obj




class Vendor(models.Model):
    name = models.CharField(max_length=50)
    # is_active=models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Vendor'
        ordering = ('-id',)

class Factory(models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 100)
    # is_active=models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Factory'
        ordering = ('-id',)

class Order(models.Model):
    ORDER_STATUSES = (('Unconfirmed', 'Placed'),
                      ('Processing', 'Processed'),
                      ('Confirmed', 'Confirmed'),
                      ('Complete', 'Completed'),
                      ('Cancelled', 'Cancelled'),
                      ('Dispatched', 'Dispatched'),
                      )
    PAYMENT_STATUSES = (('Initiated', 'Initiated'),
                        ('Awaiting Payment', 'Awaiting Payment'),
                        ('Paid', 'Paid'),
                        ('Refunded', 'Refunded'),
                        ('Partially Refunded', 'Partially Refunded'),
                        )
    PAYMENT_METHOD = (('KHALTI', 'KHALTI'),
                        ('ESEWA', 'ESEWA'),
                        ('IME', 'IME'),
                        ('CARD', 'CARD'),
                        ('COD', 'COD'),
                        ('CREDIT', 'CREDIT'),
                        ('BANK', 'BANK'),
                        ('FONEPAY', 'FONEPAY'),
                        ('COD FONEPAY', 'COD FONEPAY'),
                        ('COD ESEWA', 'COD ESEWA'),
                        ('COD KHALTI', 'COD KHALTI'),
                        )
    DELIVERY_STATUS = (('New', 'New'),
                        ('Accepted', 'Accepted'),
                        ('Picked', 'Picked'),
                        ('Complete', 'Complete'),
                        ('Cancelled', 'Cancelled'),
                        )
    ODOO_STATUS = (('None', 'None'),
                    ('Success', 'Success'),
                    ('Failed', 'Failed'),
                    ('Completed', 'Completed'),
                    ('Finished', 'Finished')
                )
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                 blank=True, related_name='customer_order', on_delete=models.CASCADE)
    order_number = models.CharField(max_length=100, unique=True)
    total = models.FloatField()
    sub_total_order = models.FloatField()
    shipping_cost = models.FloatField()
    coupon = models.CharField(max_length=50, blank=True, null=True)
    discount = models.FloatField(default=0, null=True, blank=True)
    odoo_status = models.CharField(max_length=20, choices=ODOO_STATUS, default='None', null=True, blank=True)
    odoo_db_id = models.CharField(max_length=50, null=True, blank=True)
    odoo_id = models.CharField(max_length=50, null=True, blank=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUSES)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUSES)
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_STATUS,null=True,blank=True)
    delivery_address = models.ForeignKey(DeliveryAddress, on_delete=models.PROTECT, related_name='delivery_orders')
    placed_on = models.DateField(auto_now_add=True)
    created_on = models.DateTimeField(auto_now_add=True)
    accepted_on = models.DateTimeField(blank=True,null=True)
    processed_on = models.DateTimeField(blank=True,null=True)
    delivered_on = models.DateTimeField(blank=True,null=True)
    completed_on = models.DateTimeField(blank=True,null=True)
    dispatched_on = models.DateTimeField(blank=True,null=True)
    dispatched_ready_on = models.DurationField(blank=True, null=True)
    dispatched_ready_on_time = models.DateTimeField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD,default="COD")
    # int_card_extra_charge=models.FloatField(blank=True,null=True)
    date = models.DateField(null=True,)
    time = models.ForeignKey(ShippingTime,related_name='order_shipping_time',on_delete=models.PROTECT,null=True)
    delivery_sent_nepxpress = models.BooleanField(default=False)
    delivery_assigned = models.CharField(max_length=250, blank=True, null=True)
    reference=models.CharField(max_length=50)
    vendor = models.ForeignKey(Vendor, related_name = 'vendor', on_delete=models.PROTECT, null = True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='order_created', on_delete = models.PROTECT, null=True, blank=True)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='order_updated', on_delete = models.PROTECT, null=True, blank=True)
    dispatch_ready_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='order_dispatched_by', on_delete = models.PROTECT, null=True, blank=True)
    dispatched_by =models.ForeignKey(settings.AUTH_USER_MODEL, related_name='order_dispatched', on_delete = models.PROTECT, null=True, blank=True)
    cancelled_refrence = models.CharField(max_length = 500, null=True, blank=True)
    class Meta:
        verbose_name_plural = 'Orders'
        ordering = ('-id',)

    def __str__(self):
        return str(self.order_number)

    # @property
    # def cake_in_freeze(self):
    #     import datetime
    #     return datetime.date.now()-self.dispatched_on
    

    @property
    def customerOrderLink(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current().domain+'/order-detail-to-customer/'+self.order_number
        return current_site

    def get_order_status(self):
        return next((status[1] for status in self.ORDER_STATUSES if status[0] == self.order_status), None)

    def get_payment_status(self):
        return next((status[1] for status in self.PAYMENT_STATUSES if status[0] == self.payment_status), None)

    def get_order_products_count(self):
        return self.items.count()

    def get_order_products_quantity(self):
        quantity = 0
        for item in self.items.all():
            quantity = quantity + item.quantity
        return quantity

    def get_total_with_shipping_cost(self):
        total_amount = self.total+self.shipping_cost
        return total_amount

    def sub_total(self):
        if self.sub_total_order == 0:
            return self.total - self.shipping_cost
        else:
            return self.sub_total_order

    def get_total(self):
        if self.discount:
            total = self.total +self.discount
            return total
        else:
            return self.total

    def return_paid_amount(self):
        if self.order_status == 'Paid':
            return self.total
        else:
            return 0

    def return_unpaid_amount(self):
        if self.order_status=='Awaiting Payment':
            return self.total
        else:
            return 0

    @property
    def get_order_status_array(self):
        if self.order_status == "Confirmed":
          return ["Confirmed"]
        if self.order_status == "Processing":
          return ["Confirmed","Processing"]
        # if self.order_status == "Processing":
        #   return ["Confirmed","Processing"]
        if self.order_status == "Complete":
          return ["Confirmed","Processing","Complete"]
    
    @classmethod
    def update_order_status(cls,order_id,status,remarks):
      from datetime import datetime as dt
      current_date_time = dt.now() + timedelta(hours=5.75)
      if status == "baker":
        status_ = "Dispatched"
        cls.objects.filter(id=order_id).update(order_status=status_, cancelled_refrence=remarks)
      elif status == "Confirmed":
        cls.objects.filter(id=order_id).update(order_status=status,accepted_on=current_date_time, cancelled_refrence=remarks)
      elif status == "Processing":
        cls.objects.filter(id=order_id).update(order_status=status,processed_on=current_date_time, cancelled_refrence=remarks)
      elif status == "Complete":
        cls.objects.filter(id=order_id).update(order_status=status,completed_on=current_date_time, cancelled_refrence=remarks)
      elif status == "Dispatched":
        cls.objects.filter(id=order_id).update(order_status='Dispatched',dispatched_on=current_date_time, cancelled_refrence=remarks)
      else:
        cls.objects.filter(id=order_id).update(order_status=status, cancelled_refrence=remarks)
    

    @classmethod
    def update_dispatcher(cls, order_id,status, user_id):
        from datetime import datetime as dt
        import pytz
        current_date_time = dt.now() + timedelta(hours=5.75)
        if status == "baker":
            cls.objects.filter(id=order_id).update(dispatch_ready_by=user_id, dispatched_ready_on_time=current_date_time)


    @property
    def define_color_freeze_time(self):
        from datetime import datetime as dt
        import pytz
        if self.dispatched_on:
            green_time = self.dispatched_on+timedelta(minutes=45)
            blue_time = self.dispatched_on+timedelta(hours=2)
            current_date_time = dt.now() + timedelta(hours=5.75)
            gt = green_time.replace(tzinfo=pytz.utc)
            bt = blue_time.replace(tzinfo=pytz.utc)
            cdt = current_date_time.replace(tzinfo=pytz.utc)
            if gt > cdt:
                color_  = "green"                
            elif bt > cdt:
                color_  = "blue"                
            else:
                color_ = "red"
            return color_
        else:
            return "Time Not Assigned"
    
    
    def undiscounted_sub_total(self):
        if self.discount:
            return self.sub_total_order+self.discount
        

    def undiscount_total(self):
        if self.discount:
            return self.total+self.discount
        

    def addonTotal(self):
        total = 0
        for i in self.product_varient.all():
            total = total+i.addonTotal()
        return total
    
    @property
    def store(self):
        if self.items.all().exists():
            return self.items.all()[0].product.product.store
    
    @classmethod
    def placeOrderAuth(cls,user_obj,order_number,discount,coupon,sub_total,shipping_cost,address,total,cart,unique_item,reference,date,time):
        order = cls.objects.create(customer=user_obj,
                            order_number=order_number,
                              discount=discount,
                              coupon=coupon,
                              sub_total_order = sub_total,
                              shipping_cost=shipping_cost,
                              delivery_address=address,
                              date=date,
                              time=time,
                              total=total,
                              order_status='Unconfirmed',
                              payment_status='Awaiting Payment',
                              delivery_status='New',
                              reference=reference,
                              )

    
        for item in CartItem.objects.filter(cart=cart,date=unique_item.date,time=unique_item.time,product__product__store__name=unique_item.product.product.store.name):
           time=get_object_or_404(ShippingTime,id=item.time)
           flavour=None
           for i in item.product.attribut_value.all():
            if i.attribute.name == 'Flavour':
                flavour=i.value
           order_item=OrderItem.objects.create(order=order,
                                   product=item.product,
                                   name=item.product.varient_name,
                                   flavour=flavour,
                                   price=item.product.selling_price,
                                   quantity=item.quantity,
                                   sub_total=item.get_sub_total(),
                                   total=item.get_total_with_shipping_cost(),
                                   special_instruction=item.message,
                                   is_sugerless=item.is_sugarless,
                                   is_eggless=item.is_eggless,
                                   shipping_method=item.shipping_method,
                                   photo_cake_image=item.photo_cake_image,
                                   pound=item.pound,
                                   )
           item_order=get_object_or_404(OrderItem,id=order_item.id)
           if item.item_addons:
              for i in item.item_addons.all():
                 AddonOrderItem.objects.create(order_item=item_order,
                    addons=i.addons,
                    quantity=i.quantity,
                    price = i.price
                    )

           # quantity=ProductVarient.objects.get(id=item.product.id).quantity-item.quantity
           # ProductVarient.objects.filter(id=item.product.id).update(quantity=quantity)
        return order

    @classmethod
    def get_pending_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_pending_items=0
    
        if store:
            if day=='this_week':
                objects=cls.objects.filter(date__lte=today_date,date__gte=week_initial_day,order_status='Unconfirmed',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Unconfirmed',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Unconfirmed',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Unconfirmed',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
        else:
            if day=='this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Unconfirmed').order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Unconfirmed').order_by('items__product__product__store__name','date','time__time_from')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Unconfirmed').order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Unconfirmed').order_by('items__product__product__store__name','date','time__time_from')
        total_pending_items=total_pending_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_pending_items':total_pending_items,'morning_delivery':morning_delivery_orderitem}
    
    @classmethod
    def get_confirmed_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_confirmed_items=0
    
        if store:
            if day=='this_week':
                objects=cls.objects.filter(date__lte=today_date,date__gte=week_initial_day,order_status='Confirmed',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Confirmed',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Confirmed',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Confirmed',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        else:
            if day=='this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Confirmed').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Confirmed').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Confirmed').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Confirmed').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        total_confirmed_items=total_confirmed_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_confirmed_items':total_confirmed_items,'morning_delivery':morning_delivery_orderitem}

    @classmethod
    def get_processing_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_processing_items=0
        if store:
            if day=='this_week':
                objects = cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Processing',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects = cls.objects.filter(date=date_filter_order,order_status='Processing',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects = cls.objects.filter(date__gte=week_initial_day,order_status='Processing',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects = cls.objects.filter(date=today_date,order_status='Processing',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        else:
            if day == 'this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Processing').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Processing').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Processing').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Processing').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        total_processing_items=total_processing_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_procesing_items':total_processing_items,'morning_delivery':morning_delivery_orderitem}

    @classmethod
    def get_dispatched_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_dispatched_items=0
        if store:
            if day=='this_week':
                objects = cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Dispatched',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                if date_filter_order:
                    objects = cls.objects.filter(date=date_filter_order,order_status='Dispatched',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
                else:
                    objects = cls.objects.filter(date__gte=week_initial_day,order_status='Dispatched',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects = cls.objects.filter(date=today_date,order_status='Dispatched',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
        else:
            if day == 'this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Dispatched').order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Dispatched').order_by('items__product__product__store__name','date','time__time_from')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Dispatched').order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Dispatched').order_by('items__product__product__store__name','date','time__time_from')
        total_dispatched_items=total_dispatched_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_dispatched_items':total_dispatched_items,'morning_delivery':morning_delivery_orderitem}
    
    @classmethod
    def get_complete_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_complete_items=0
        if store:
            if day == 'this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Complete',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Complete',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Complete',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Complete',items__product__product__store__slug=store.slug).order_by('items__product__product__store__name','date','time__time_from')
        else:
            if day == 'this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Complete').order_by('items__product__product__store__name','date','time__time_from')
            elif day == 'all':
                objects=cls.objects.filter(date__gte=week_initial_day,order_status='Complete').order_by('items__product__product__store__name','date','time__time_from')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Complete').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        total_complete_items=total_complete_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_complete_items':total_complete_items,'morning_delivery':morning_delivery_orderitem}


    '''For sales report'''
    @classmethod
    def sales_by_costumer_all_data(cls, order_num):
        costumer_name = cls.objects.filter(order_number=order_num).values('delivery_address__receiver_fullname')
        contact_number = cls.objects.filter(order_number=order_num).values('delivery_address__contact_number')
        placed_on = cls.objects.filter(order_number=order_num).values('placed_on')
        quantity = OrderItem.objects.filter(order__order_number=order_num).values('quantity').count()
        item_count = OrderItem.objects.filter(order__order_number=order_num).values('product__varient_name').count()
        other_data = cls.objects.filter(order_number=order_num).values('total', 'sub_total_order', 'shipping_cost', 'payment_status', 'discount')
        gross_sells = other_data[0]['total']
        shipping_cost = other_data[0]['shipping_cost']
        discounts = other_data[0]['discount']
        status = other_data[0]['payment_status']
        net_sells = (other_data[0]['sub_total_order']+shipping_cost)-discounts
        return costumer_name, contact_number, placed_on, quantity, item_count, gross_sells, shipping_cost, discounts, status, net_sells



    @classmethod
    def sells_over_time_all_data(cls,date):
        # date = cls.objects.values('placed_on')
        total = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(created_on__date=date).count()
        total_paid = cls.objects.filter(created_on__date=date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(created_on__date=date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('shipping_cost'))
        return total, item_count, total_paid, total_unpaid,discounts, shipping


    @classmethod
    def sells_over_time(cls,date):
        # date = cls.objects.values('placed_on')
        total = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(created_on__date=date).count()
        total_paid = cls.objects.filter(created_on__date=date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(created_on__date=date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(created_on__date=date).aggregate(total_price=Sum('shipping_cost'))
        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price'] = 0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'date':date,
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })
        return new_list

    @classmethod
    def sells_over_time_week(cls,date):
        # date = cls.objects.values('placed_on')
        total = cls.objects.filter(placed_on__year =datetime.today().year , placed_on__week=date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(placed_on__year =datetime.today().year,placed_on__week=date).count()
        total_paid = cls.objects.filter(placed_on__year =datetime.today().year, placed_on__week=date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(placed_on__year =datetime.today().year, placed_on__week=date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(placed_on__year =datetime.today().year, placed_on__week=date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(placed_on__year =datetime.today().year, placed_on__week=date).aggregate(total_price=Sum('shipping_cost'))

        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'date':date,
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })
        return new_list

    @classmethod
    def sells_over_time_month(cls,date):
        # date = cls.objects.values('placed_on')
        total = cls.objects.filter(placed_on__year =datetime.today().year ,created_on__month=date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(placed_on__year =datetime.today().year ,created_on__month=date).count()
        total_paid = cls.objects.filter(created_on__month=date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(placed_on__year =datetime.today().year ,created_on__month=date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(placed_on__year =datetime.today().year ,created_on__month=date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(placed_on__year =datetime.today().year ,created_on__month=date).aggregate(total_price=Sum('shipping_cost'))

        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'date':date,
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })
        return new_list

    @classmethod
    def sells_over_time_year(cls,date):
        # date = cls.objects.values('placed_on')
        total = cls.objects.filter(created_on__year=date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(created_on__year=date).count()
        total_paid = cls.objects.filter(created_on__year=date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(created_on__year=date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(created_on__year=date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(created_on__year=date).aggregate(total_price=Sum('shipping_cost'))
        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'date':date,
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })

        return new_list


    @classmethod
    def sells_over_time_date_range(cls,start_date, end_date):
        total = cls.objects.filter(placed_on__range=[start_date, end_date], order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(placed_on__range=[start_date, end_date], order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
        total_paid = cls.objects.filter(placed_on__range=[start_date, end_date], payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(placed_on__range=[start_date,end_date], payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(placed_on__range=[start_date, end_date], order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(placed_on__range=[start_date, end_date], order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))
        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'status':f'{start_date}-to-{end_date}',
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })

        return new_list


    @classmethod
    def sells_over_time_range_on_date(cls,start_date):
        total = cls.objects.filter(placed_on=start_date).aggregate(total_price=Sum('total'))
        item_count = cls.objects.filter(placed_on=start_date).count()
        total_paid = cls.objects.filter(placed_on=start_date, payment_status="Paid").aggregate(total_price=Sum('total'))
        total_unpaid = cls.objects.filter(placed_on=start_date, payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
        discounts = cls.objects.filter(placed_on=start_date).aggregate(total_price=Sum('discount'))
        shipping = cls.objects.filter(placed_on=start_date).aggregate(total_price=Sum('shipping_cost'))

        new_list = []
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])
        new_list.append({
            'status':start_date,
            'item_count':item_count,
            'total':total['total_price'],
            'discount': discounts['total_price'],
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'shipping':shipping['total_price'],
            'net_sells': net_sells,
        })

        return new_list



    @classmethod
    def get_cancelled_order_items(cls,today_date,store,day,date_filter_order):
        from datetime import date as d
        week_initial_day = d.today()
        morning_delivery_orderitem={}
        total_cancelled_items=0
    
        if store:
            if day=='this_week':
                objects=cls.objects.filter(date__lte=today_date,date__gte=week_initial_day,order_status='Cancelled',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Cancelled',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Cancelled',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Cancelled',items__product__product__store__slug=store.slug).order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        else:
            if day=='this_week':
                objects=cls.objects.filter(date__gte=week_initial_day,date__lte=today_date,order_status='Cancelled').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            elif day == 'all':
                if date_filter_order:
                    objects=cls.objects.filter(date=date_filter_order,order_status='Cancelled').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
                else:
                    objects=cls.objects.filter(date__gte=week_initial_day,order_status='Cancelled').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
            else:
                objects=cls.objects.filter(date=today_date,order_status='Cancelled').order_by('delivery_order__pickup_date','delivery_order__pickup_time')
        total_cancelled_items=total_cancelled_items+objects.count()
        morning_delivery_orderitem.update({'items':objects})
        return {'total_cancelled_items':total_cancelled_items,'morning_delivery':morning_delivery_orderitem}
    
    @property
    def pickup_date(self):
        if self.delivery_order:
            return self.delivery_order.pickup_date
        else:
            return 'Not assigned'
    
    @property
    def pickup_time(self):
        if self.delivery_order:
            return self.delivery_order.pickup_time
        else:
            return 'Not assigned'
    @property
    def delivery_boy(self):
        if self.delivery_order:
            return self.delivery_order.user.email
        else:
            return 'Not assigned'
    @property
    def created_on_nepal_time(self):
        import datetime
        hours_added = datetime.timedelta(hours = 5.75)
        return self.created_on + hours_added

    @property
    def dispatched_on_npt(self):
        import datetime
        import pytz
        if self.dispatched_on:
            hours_added = datetime.timedelta(hours=5.75)
            dis_time = (self.dispatched_on-hours_added).replace(tzinfo=pytz.utc)
            return dis_time
        else:
            return None

    @property
    def delivered_on_npt(self):
        import datetime
        import pytz
        if self.delivered_on:
            hours_added = datetime.timedelta(hours=5.75)
            dis_time = (self.delivered_on-hours_added).replace(tzinfo=pytz.utc)
            return dis_time
        else:
            return None

    @property
    def complete_on_npt(self):
        import datetime
        import pytz
        if self.completed_on:
            hours_added = datetime.timedelta(hours=5.75)
            dis_time = (self.completed_on-hours_added).replace(tzinfo=pytz.utc)
            return dis_time
        else:
            return None

    @property
    def ready_to_dispatched_by(self):
        order_number = self.order_number
        dispatcher_name = OrderDelivery.objects.filter(order__order_number=order_number).values('user__username')
        if dispatcher_name:
            return dispatcher_name
        else:
            return None

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(ProductVarient, related_name='product_varient', on_delete=models.PROTECT)
    name = models.CharField(max_length=100, null=True, blank=True)
    flavour = models.CharField(max_length=50, null=True, blank=True)
    price = models.FloatField(help_text='Unit price of the product')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    sub_total = models.FloatField()
    total = models.FloatField()
    special_instruction = models.TextField(max_length=400, blank=True, null=True)
    is_sugerless = models.BooleanField()
    is_eggless = models.BooleanField()
    shipping_method = models.ForeignKey(ShippingMethod, related_name='orderitem_shipping_method', on_delete=models.PROTECT)
    pound = models.FloatField()
    # flavour = models.FloatField()
    photo_cake_image = models.ImageField(
        upload_to='cart/photocake/', blank=True, null=True, max_length=700)
    photo_cake_image1 = models.ImageField(
        upload_to='cart/photocake/', blank=True, null=True, max_length=700)
    photo_cake_image2 = models.ImageField(
        upload_to='cart/photocake/', blank=True, null=True, max_length=700)
    photo_cake_image3 = models.ImageField(
        upload_to='cart/photocake/', blank=True, null=True, max_length=700)
    
    class Meta:
        db_table = 'sales_order_item'
        verbose_name_plural = 'Order Items'
        ordering = ('-id',)
    
    def total_price_of_product(self):
        return self.price * self.quantity

    def shipping_cost(self):
        return self.total-(self.sub_total)

    def __str__(self):
        return self.order.order_number

    @property
    def addonTotal(self):
        total=0
        for i in self.orderitem_addons.all():
            total = total+i.price*i.quantity
        return total
    
    def sub_total_without_addon(self):
        return self.sub_total-self.addonTotal

    def productTotalWithAddons(self):
        total = self.total_price_of_product()+self.quantity*self.addonTotal()


    @classmethod
    def customer_purchased_item(cls,user,product):
        return cls.objects.filter(order__customer=user,product__product__name=product,order__order_status='Complete').exists()

    @property
    def product_varient_name(self):
        return f"{self.product.varient_name}"


class AddonOrderItem(models.Model):
    order_item = models.ForeignKey(
        OrderItem, related_name='orderitem_addons', on_delete=models.CASCADE)
    addons = models.ForeignKey(
        ProductAddons, related_name='product_addons', null=True, on_delete=models.PROTECT)
    quantity = models.IntegerField()
    price = models.IntegerField(null = True, blank =True)

    def total(self):
        return self.quantity*self.price


class DeliveryNepxpress(models.Model):
    order_number = models.CharField(max_length=100, blank=True, null=True)
    activity = models.CharField(max_length=900, blank=True, null=True)
    comment = models.CharField(max_length=900, blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)


class OrderDelivery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='delivery_person', on_delete=models.PROTECT,null=True,blank=True)
    order = models.OneToOneField(Order, related_name='delivery_order', on_delete=models.CASCADE)
    pickup_date=models.DateField()
    pickup_time=models.TimeField()
    expected_delivery_time=models.TimeField(null = True, blank = True)
    # factory = models.ForeignKey(Factory, related_name = 'factory_delivery_order', null=True, blank=True, on_delete = models.PROTECT)
    factory = models.ForeignKey(Factories, related_name = 'factory_delivery_order', null=True, blank=True, on_delete = models.PROTECT)
    store=models.ForeignKey(Store,related_name='order_delivery_store', on_delete=models.PROTECT)
    remarks = models.TextField(null=True, blank =True)
    def __str__(self):
        return f"{self.order.order_number}"

    def deliveryBoyLink(self):
        from django.contrib.sites.models import Site
        if self.user:
            current_site = Site.objects.get_current().domain+'/order/assigned-to-delivery-boy/'+str(self.user.id)
            return current_site
        else:
            return False

    @classmethod 
    def storeList(cls,user,today):
        return Store.objects.filter(order_delivery_store__user=user,order_delivery_store__pickup_date=today,order_delivery_store__order__order_status__in=['Processing','Dispatched']).distinct()



class OrderAlert(models.Model):
    start_time  = models.TimeField()
    end_time = models.TimeField()
    threshold = models.IntegerField(default=20)

    class Meta:
        verbose_name = "Order Alert"
        verbose_name_plural = "Order Alerts"

    def __str__(self):
        return str(self.threshold)

    @classmethod
    def distinct_order(cls,day,date):
        obj = OrderAlert.objects.all()
        from datetime import date as d
        week_initial_day=d.today()
        data_list = []
        for i in obj:
            data = {}
            data['start_time'] = i.start_time
            data['end_time'] = i.end_time
            data['threshold'] = i.threshold
            if day == 'this_week':
                data['threshold'] = i.threshold * 7
                delivery_count = Order.objects.filter(date__gte=week_initial_day,date__lte=date,delivery_order__expected_delivery_time__gte=i.start_time,delivery_order__expected_delivery_time__lt=i.end_time)
                delivery_count = delivery_count.filter(~Q(order_status = 'Cancelled')).count()
            elif day == 'all':
                delivery_count = Order.objects.filter(date__gte=week_initial_day,delivery_order__expected_delivery_time__gte=i.start_time,delivery_order__expected_delivery_time__lt=i.end_time)
                delivery_count = delivery_count.filter(~Q(order_status = 'Cancelled')).count()
            else:
                delivery_count = Order.objects.filter(date=date,delivery_order__expected_delivery_time__gte=i.start_time,delivery_order__expected_delivery_time__lt=i.end_time)
                delivery_count = delivery_count.filter(~Q(order_status = 'Cancelled')).count()
            data['delivery_count'] = delivery_count
            data_list.append(data)
            if delivery_count >= data['threshold']:
                data['alert'] = True
            else:
                data['alert'] = False
            data = {}
        return data_list

class OrderAssignedToVendor(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='vendor', on_delete=models.PROTECT,null=True,blank=True)
    order = models.OneToOneField(Order, related_name='vendor_assigned_order', on_delete=models.CASCADE)

import jsonfield

class OrderLogs(models.Model):
    order = models.ForeignKey(Order, related_name='order_log', on_delete=models.CASCADE)
    log_created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_order_item_logs', on_delete=models.PROTECT,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    order_data_log = jsonfield.JSONField()
    order_item = jsonfield.JSONField()
    addons = jsonfield.JSONField()
