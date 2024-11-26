from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register('list-cart',ListRetrieveCartView,basename='get-cart')
router.register('post-cart',CreateUpdateDestroyCartView,basename='cart-write')
router.register('get-cartitem',ListRetrieveCartItemView,basename='cartitem-read')
router.register('post-cartitem',CreateUpdateDestroyCartItemView,basename='cart-item-write')
router.register('get-orders',ListRetrieveOrderView,basename='get-orders')
router.register('post-orders',CreateUpdateDestroyOrderView)

# router.register('orders',OrderView,basename='orders')
# router.register('delivery',DeliveryNepView,basename='delivery')



urlpatterns = [

path('',include(router.urls)),
# path('get-cart/<coupon>/',calculation_of_coupon,name='list-cart'),
path('apply-coupon/',applycoupon,name='apply-coupon'),
path('checkout-cart/',checkoutcart,name='checkout-cart'),

path('order/assigned-to-delivery-boy/<int:user>/',DeliveryOrderAssignedToDeliveryBoy.as_view(),name='user-assigned-delivery'),
path('order/delivery-status/change/',OrderITemDeliveryStatusChange.as_view(),name='change-delivery-status'),
path('order/to/vendor/<slug:slug>/',SendingDetailToVendor.as_view(),name='get-vendor-order'),

]
