from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('get-put-delete-contact-message',RetrieveUpdateDestroyContactMessageView,basename='rud-message')
router.register('get-put-delete-email',RetrieveUpdateDestroyContactSubscriptionEmailView,basename='rud-email')

urlpatterns = [

path('',include(router.urls)),
path('create-email/',CreateSubscriptionEmailView.as_view()),
path('create-message/',CreateContactMessageView.as_view()),

]
