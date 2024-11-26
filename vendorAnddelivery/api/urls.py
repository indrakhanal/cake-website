from django.urls import path, include
from rest_framework import routers
from .views import *

urlpatterns = [

path('order/vendor/list/', VendorView.as_view()),
path('order/delivery-boy/',DeliveryBoyView.as_view()),
path('order/dispatcher/',OrderDispatcherView.as_view()),
]
