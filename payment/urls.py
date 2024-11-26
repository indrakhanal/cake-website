from django.urls import path
from django.views.generic import TemplateView
from .views import *
from payment.payment_validation import *
app_name = 'payment'

urlpatterns = [

path('khalti-payment/',khalti_payment,name='khalti-payment'),
path('esewa-payment/',esewa_payment,name='esewa-payment'),
path('request-ime-creds/',request_ime_credentials,name='request-ime-creds'),
path('ime-payment/',ime_payment,name='ime-payment'),
path('initiate-payment/',initiate_esewa_payment_order,name='init-payment'),
path('payment-failed/',payment_failed,name='payment-failed'),

path('card-checkout/',NICPayment.as_view(),name='card-checkout'),
path('card-checkout-response/',NICPaymentResponse.as_view(),name='card-checkout-response'),
path('payment-failed/',nic_checkout_cancelled,name='card-checkout-cancelled'),
path('ime-checkout-cancelled/',ime_checkout_cancelled,name='ime-checkout-cancelled'),

path('pay/',TemplateView.as_view(template_name='admin_view/payment_display.html'),name='khalti'),
path('pay/update/',TemplateView.as_view(template_name='admin_view/payment_update.html')),
path('payment/list/',paymentList,name='payment-list'),
path('payment/create/',paymentCreate,name='payment-create'),
path('payment/available/status',paymentAvailableStatus,name='payment-available'),

path('payment-failed-card/',PaymentFailedNIC.as_view(),name='payment-failed-card'),



]
