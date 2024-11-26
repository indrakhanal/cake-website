from rest_framework import serializers
from marketing.models import *


class CartCouponSerializer(serializers.ModelSerializer):
   class Meta:
      model = CartCoupon
      fields = '__all__'

