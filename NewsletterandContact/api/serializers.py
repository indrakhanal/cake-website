from rest_framework import serializers
from NewsletterandContact.models import *


class SubscriptionEmailSerializer(serializers.ModelSerializer):
   class Meta:
      model = SubscriptionEmail
      fields = '__all__'

class ContactMessageSerializer(serializers.ModelSerializer):
   class Meta:
      model = ContactMessage
      fields = '__all__'
