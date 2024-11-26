from sales.models import Order, OrderDelivery
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.generics import ListAPIView
from django.forms.models import model_to_dict
from datetime import date, datetime, timezone, timedelta
from .permissions import *

class VendorView(ListAPIView):
	serializer_class = VendorSerializer
	queryset = Order.objects.filter(order_status__in=['Confirmed','Processing','Dispatched']).order_by('-order_status','delivery_order__pickup_time')
	filterset_fields = ['date']
	permission_classes = [IsVendor]

class DeliveryBoyView(ListAPIView):
	serializer_class = DeliveryBoySerializer
	queryset=OrderDelivery.objects.filter(user=self.kwargs['user'],order__order_status__in=['Processing','Dispatched','Complete']).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
	filterset_fields = ['pickup_date']
	permission_classes = [IsDeliveryBoy]

class OrderDispatcherView(ListAPIView):
	serializer_class = OrderDispatcherSerializer
	queryset = Order.objects.filter(order_status__in=['Dispatched']).order_by('-delivery_order__user','delivery_order__expected_delivery_time')
	filterset_fields = ['date']
	permission_classes = [IsDispatcher]