from django.shortcuts import render
from rest_framework import viewsets,permissions,mixins
from marketing.models import *
from .serializers import *
import django_filters

class CartCouponFilter(django_filters.FilterSet):
    class Meta:
        model = CartCoupon
        fields = ['is_active']
class CartCouponView(viewsets.ModelViewSet):
   queryset = CartCoupon.objects.order_by('-id').all()
   serializer_class = CartCouponSerializer
   permission_classes = (permissions.IsAdminUser,)
   filter_class = CartCouponFilter
