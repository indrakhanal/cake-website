from rest_framework import serializers
from sales.models import *
from settings.models import ShippingTime
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ['id','first_name', 'last_name']

class DeliveryAddressSerializer(serializers.ModelSerializer):
	class Meta:
		model = DeliveryAddress
		fields = ['receiver_fullname',
		'receiver_email',
		'receiver_delivery_address',
		'receiver_landmark','receiver_city','receiver_area','receiver_contact_number1','receiver_contact_number2',
		'sender_fullname',
		'sender_email',
		'sender_address',
		'contact_number',
		'hide_info_from_receiver',]

class ShippingTimeSerializer(serializers.ModelSerializer):
	class Meta:
		model = ShippingTime
		fields = ['id', 'time_from', 'time_to']

class VendorSerializer(serializers.ModelSerializer):
	delivery_address = DeliveryAddressSerializer()
	time = ShippingTimeSerializer()
	class Meta:
		model = Order
		fields = ['id',
		'order_number',
		'total',
		'sub_total_order',
		'order_status',
		'payment_status',
		'delivery_status',
		'date',
		'time',
		'delivery_assigned',
		'vendor',
		'remarks',
		'delivery_address'
		]

class DeliveryBoySerializer(serializers.ModelSerializer):
	order = VendorSerializer()
	class Meta:
		model = OrderDelivery
		fields = ['id','user','order','pickup_date','pickup_time','expected_delivery_time','remarks','factory__name']

class DispatcherSerializer(serializers.ModelSerializer):
	delivery_address = DeliveryAddressSerializer()
	time = ShippingTimeSerializer()
	class Meta:
		model = Order
		fields = ['id',
		'order_number',
		'total',
		'sub_total_order',
		'order_status',
		'payment_status',
		'delivery_status',
		'date',
		'time',
		'delivery_assigned',
		'vendor',
		'remarks',
		'delivery_address'
		]