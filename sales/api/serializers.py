from rest_framework import serializers
from sales.models import *
from catalog.models import *
from catalog.api.serializers import *
from settings.api.serializers import ShippingMethodWriteSerializer


class CartItemReadSerializer(serializers.ModelSerializer):
   # cart = CartSerializer(many=False,read_only=False)
   product = ProductVarientWriteSerializer(many=False,read_only=False)
   shipping_method = ShippingMethodWriteSerializer(many=False,read_only=True)
   class Meta:
      model = CartItem
      fields = '__all__'

class CartItemWriteSerializer(serializers.ModelSerializer):
   # is_eggless = serializers.BooleanField(required=False)
   # is_sugarless = serializers.BooleanField(required=False)
   class Meta:
      model = CartItem
      fields = ('id','quantity','product','date','time','message','shipping_method','is_eggless','is_sugarless','pound','photo_cake_image',)
      extra_kwargs = {
          'is_eggless': {'required': True, 'allow_null': False},
        }

class CartSerializer(serializers.ModelSerializer):
   # items = CartItemWriteSerializer(many=True,read_only=False)
   class Meta:
      model = Cart
      fields = ('id','coupon',)

class CartTestSerializer(serializers.ModelSerializer):
   # varient =ProductVarientWriteSerializer(many=True,read_only=True)
   items = CartItemReadSerializer(many=True,read_only=True)
   class Meta:
      model = Cart
      fields = ('coupon','items','varient')
      depth=1

      # def to_representation(self, instance):
      #   identifiers = dict()
      #   identifiers['items'] = instance.items
      #   for i in identifiers['items']:
      #      print('items',i)
      #   identifiers['varient'] = instance.instance
      #   print('varient',identifiers[varient])

      #   representation = {
      #       'identifiers': identifiers,
      #    } 

      #   return representation
      


class DeliveryAddressSerializer(serializers.ModelSerializer):
   class Meta:
      model = DeliveryAddress
      fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
   product = ProductVarientWriteSerializer(many=False,write_only=True)
   addons = ProductAddonsSerializer(many=True,read_only=True)
   shipping_method = ShippingMethodWriteSerializer(many=False,read_only=True)
   class Meta:
      model = OrderItem
      fields = '__all__'

class OrderReadSerializer(serializers.ModelSerializer):
   delivery_address = DeliveryAddressSerializer(many=False,read_only=True)
   items = OrderItemSerializer(many=True,read_only=True)
   class Meta:
      model = Order
      fields = '__all__'
      # fields = ('id','customer','order_number','total','shipping_cost','coupon','discount','refunded_amount','order_status','payment_status','delivery_address','customer_notes','created_on',
      #          'order_from','items')
class OrderWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Order
      fields = '__all__'
      # fields = ('id','customer','order_number','total','sub_total_order','shipping_cost','coupon','discount','refunded_amount','order_status','payment_status','delivery_address','customer_notes','created_on',
      #          'order_from','items')


class OrderItemSerializer(serializers.ModelSerializer):
   product = ProductWriteSerializer(many=False,read_only=True)
   class Meta:
      model = OrderItem
      fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
   delivery_address = DeliveryAddressSerializer(many=False,read_only=True)
   items = OrderItemSerializer(many=True,read_only=True)
   class Meta:
      model = Order
      fields = ('id','customer','order_number','total','shipping_cost','coupon','discount','refunded_amount','order_status','payment_status','delivery_address','customer_notes','created_on',
               'order_from','items')

class AddonOrderItemSerializer(serializers.ModelSerializer):
   addons=ProductAddonsSerializer(many=False,read_only=True)
   class Meta:
      model=AddonOrderItem
      fields=['addons','quantity']
      

class DeliveryNepSerializer(serializers.ModelSerializer):
   class Meta:
      model = DeliveryNepxpress
      fields = '__all__'

class ReceiverDeliveryAddressSerializer(serializers.ModelSerializer):
   class Meta:
      model=DeliveryAddress
      fields=['receiver_fullname','receiver_email','receiver_delivery_address','receiver_landmark','receiver_address_type','receiver_contact_number1','receiver_contact_number2']


class OrderItemsSerializer(serializers.ModelSerializer):
   product_varient=serializers.ReadOnlyField()
   orderitem_addons=AddonOrderItemSerializer(read_only=True,many=True)
   order=OrderSerializer(read_only=True)
   class Meta:
      model=OrderItem
      fields=['order','photo_cake_image','quantity','payment_status','delivery_status','product_varient','orderitem_addons','is_sugerless','is_eggless']



class OrderItemDetailSerializer(serializers.ModelSerializer):
   product_varient=serializers.ReadOnlyField()
   product_varient_name=serializers.ReadOnlyField()
   orderitem_addons=AddonOrderItemSerializer(read_only=True,many=True)
   class Meta:
      model=OrderItem
      fields=['product_varient_name','photo_cake_image','quantity','pound','product_varient','orderitem_addons','is_sugerless','is_eggless','special_instruction','price','quantity','sub_total','total']

"""Serializer to send detail of order to vendor"""
class VendorOrderSerializer(serializers.ModelSerializer):
   items=OrderItemDetailSerializer(read_only=True,many=True)
   pickup_date=serializers.ReadOnlyField()
   pickup_time=serializers.ReadOnlyField()
   delivery_boy=serializers.ReadOnlyField()
   class Meta:
      model=Order
      fields=['order_number','items','delivery_status','order_status','pickup_date','pickup_time','delivery_boy']

from store.api.serializers import StoreSerializers
class OrderDeliverySerializer(serializers.ModelSerializer):
   store = StoreSerializers(read_only=True)
   order= VendorOrderSerializer(read_only=True)
   class Meta:
      model=OrderDelivery
      fields=['user','order','store',]

from settings.models import ShippingTime
class TimeSerializer(serializers.ModelSerializer):
   class Meta:
      model=ShippingTime
      fields=['time_from','time_to']


"""Order detail serializer used in kanban during order processing"""
class OrderDetailSerializer(serializers.ModelSerializer):
   delivery_boy=serializers.ReadOnlyField()
   pickup_date=serializers.ReadOnlyField()
   pickup_time=serializers.ReadOnlyField()
   time=TimeSerializer(read_only=True,many=False)
   items=OrderItemDetailSerializer(read_only=True,many=True)
   delivery_address=ReceiverDeliveryAddressSerializer(read_only=True)
   class Meta:
      model=Order
      fields=['id','order_number','reference','payment_method','order_status','payment_status','delivery_status','delivery_address','items','date','time','pickup_time','pickup_date','delivery_boy']