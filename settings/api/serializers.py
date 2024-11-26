from rest_framework import serializers
from settings.models import *

class ShippingTimeSerializer(serializers.ModelSerializer):
   class Meta:
      model = ShippingTime
      fields = '__all__'

class ShippingMethodReadSerializer(serializers.ModelSerializer):
	shipping_time = ShippingTimeSerializer(many=True,read_only=True)
	class Meta:
		model = ShippingMethod
		fields = '__all__'


class ShippingMethodWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = ShippingMethod
      fields = '__all__'

class SettingsSerializer(serializers.ModelSerializer):
   class Meta:
      model = Settings
      fields = '__all__'

class OutletBranchSerializer(serializers.ModelSerializer):
   class Meta:
      model = OutletBranch
      fields = '__all__'
