from django.urls import path
from .views import *

app_name = 'vendorAndDelivery'

urlpatterns = [
path('app/login/',loginMain,name='app-login'),
path('order/vendor/',VendorView.as_view(),name='get-vendor-order'),
path('order/delivery/<int:user>/',DeliveryBoyView.as_view(),name='user-assigned-delivery'),
path('vendor/login/',vendorLogin,name='login-as-vendor'),
path('dispatcher/login/',dispatcherLogin,name='login-as-dispatcher'),
path('order/delivery-status/change/',OrderItemDeliveryStatusChange.as_view(),name='change-delivery-status'),
path('order/payment-method/change/',OrderItemPaymentMethodChange.as_view(),name='change-payment-method'),
path('order-status/change/',OrderStatusChange.as_view(),name='change-order-status'),
path('order/dispatcher/',OrderDispatcher.as_view(),name='dispatcher-page'),
path('delivery/login/',deliveryBoyLogin,name='login-as-delivery-boy'),
path('dispatcher/assign-delivery-boy/<int:pk>/',AssignDeliveryBoy.as_view(),name='assign-delivery-boy'),
path('ajax/get/user/',GetDeliveryUser ,name="get-delivery-user"),
path('production/login/', productionManagerLogin, name="login-as-production"),
path('order/production', ProductionManagerView.as_view(), name="get-production-manager"),
path('order/user/delivery/', getOrderUser, name="get-order-user"),


# path('assign-order-to-vendor/',assignOrderToVendor,name='assign-vendor-to-order'),
]