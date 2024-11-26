
from django.shortcuts import render
from rest_framework import viewsets,permissions,mixins
from NewsletterandContact.models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics

class CreateSubscriptionEmailView(generics.CreateAPIView):
    queryset = SubscriptionEmail.objects.order_by('-id').all()
    serializer_class = SubscriptionEmailSerializer


class RetrieveUpdateDestroyContactSubscriptionEmailView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = SubscriptionEmail.objects.order_by('-id').all()
   serializer_class = SubscriptionEmailSerializer
   permission_classes = (permissions.IsAdminUser,)

class CreateContactMessageView(generics.CreateAPIView):
   queryset = ContactMessage.objects.order_by('-id').all()
   serializer_class = ContactMessageSerializer

class RetrieveUpdateDestroyContactMessageView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = ContactMessage.objects.order_by('-id').all()
   serializer_class = ContactMessageSerializer
   permission_classes = (permissions.IsAdminUser,)
   