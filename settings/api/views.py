from django.shortcuts import render
from rest_framework import viewsets,permissions,mixins
from store.models import *
from .serializers import *
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed

class SettingsFilter(django_filters.FilterSet):
    class Meta:
        model = Settings
        fields = ['outlet_name','apply_extra_charge','flat_delivery','is_conditional_delivery_charge','is_locations_delivery_charge']
class ListRetrieveSettingsView(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = Settings.objects.order_by('-id').all()
    serializer_class = SettingsSerializer
    filter_class = SettingsFilter
    # permission_classes = (permissions.IsAdminUser)
    def get_permissions(self):
      methods = ['list','retrieve']
      permission_classes=[]
      if self.action in methods:
         permission_classes = [permissions.IsAdminUser]
      return [permission() for permission in permission_classes]

class CreateUpdateDestroySettingsView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Settings.objects.order_by('-id').all()
   serializer_class = SettingsSerializer
   permission_classes = (permissions.IsAdminUser,)

class ListRetrieveOutletBranchView(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    queryset = OutletBranch.objects.order_by('-id').all()
    serializer_class = OutletBranchSerializer
    def get_permissions(self):
      methods = ['list','retrieve']
      permission_classes=[]
      if self.action in methods:
         permission_classes = [permissions.IsAdminUser]
      return [permission() for permission in permission_classes]

class CreateUpdateDestroyOutletBranchView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = OutletBranch.objects.order_by('-id').all()
   serializer_class = OutletBranchSerializer
   permission_classes = (permissions.IsAdminUser,)


class ListRetrieveShippingTimeView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = ShippingTime.objects.order_by('-id').all()
    serializer_class = ShippingTimeSerializer
    # filter_class = CategoryFilter



class CreateUpdateDestroyShippingTimeView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = ShippingTime.objects.order_by('-id').all()
   serializer_class = ShippingTimeSerializer
   permission_classes = (permissions.IsAdminUser,)

class ListRetrieveShippingMethodView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = ShippingMethod.objects.order_by('-id').all()
    serializer_class = ShippingMethodReadSerializer
    # filter_class = CategoryFilter



class CreateUpdateDestroyShippingMethodView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = ShippingMethod.objects.order_by('-id').all()
   serializer_class = ShippingMethodWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

