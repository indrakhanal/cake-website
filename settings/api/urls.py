from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register('get-settings',ListRetrieveSettingsView)
router.register('post-settings',CreateUpdateDestroySettingsView)
router.register('get-outlet-branch',ListRetrieveOutletBranchView)
router.register('post-outlet-branch',CreateUpdateDestroyOutletBranchView)
router.register('get-shipping-time',ListRetrieveShippingTimeView)
router.register('post-shipping-time',CreateUpdateDestroyShippingTimeView)
router.register('get-shipping-method',ListRetrieveShippingMethodView)
router.register('post-shipping-method',CreateUpdateDestroyShippingMethodView)

urlpatterns = [

path('',include(router.urls)),


]
