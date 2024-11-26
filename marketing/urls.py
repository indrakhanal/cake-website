from django.urls import path
from django.views.generic import TemplateView
from .views import *
# from .views import *
app_name = 'marketing'

urlpatterns = [
path('coupons/',couponList,name="coupons-list"),
path('coupons/delete/<int:pk>/',couponDelete,name="coupon-delete"),
path('coupons-create/',couponCreate,name="coupon-create"),
path('coupons-update/<int:pk>/',couponUpdate,name="coupon-update"),
path('coupon/bulk/delete/',deleteCouponBulk,name='coupon-bulk-delete'),
path('ajax/coupon/status/update/',proAvailableStatus,name='pro-available-status'),
path('ajax/get-category-product/',getCategoryProduct,name='category-product-list')




]
