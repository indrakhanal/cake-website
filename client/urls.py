from django.urls import path
from .views import *
from django.views.generic import TemplateView

app_name = 'client'

urlpatterns = [




    path('product/review/<int:id>/',ProductReviewView.as_view(),name="product-review"),
    # path('store/review/<int:id>/',StoreReviewView.as_view(),name="store-review"),

    path('client/profile/', ClientProfile.as_view(), name="client-profile"),
    path('client/orders/', ClientOrders.as_view(), name="client-orders"),
    path('cart/', CheckoutCartView.as_view(), name="client-cart"),
    path('product/detail/<slug:slug>/', ProductDetailView.as_view(), name="product-detail"),
    path('', CatalogView.as_view(), name='catalog'),
    path('order/success/<str:reference>/', OrderSuccess.as_view(), name='order-success'),
    path('categories/product/<slug:slug>/', CategoryProduct.as_view(), name='category-product'),
    path('location/products/', LocationProduct.as_view(), name='location-products'),
    path('store/products/<slug:slug>/', StoreProductList.as_view(), name='store-product-list'),
    path('flavour/<slug:slug>/products/', FlavourProductList.as_view(), name='flavour-product-lists'),
    path('occasion/<slug:slug>/products/', OccasionProductList.as_view(), name='occasion-product-lists'),
    path('price/range/products/', PriceRangeList.as_view(), name='price-range-product-lists'),
    path('product/search/', SearchProduct.as_view(), name='product-search'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('track/order/', TrackOrder.as_view(), name='track-order'),
    # path('storelists/', StoreList.as_view(), name='stores-list-client'),
    path('ajax/cart/update/quantity/', cartQuantityUpdate, name="cart-update"),

    path('subscribe/newsletter/', subscribe, name='subscribe'),
    path('order/placed/', placeOrder, name='place-order'),
    path('order/canceled/', cancelOrder, name='cancel-order'),
    path('coupon/apply/', applyCoupon, name='apply-coupon'),
    path('send/email/', send_email_ajax, name='send-email'),
    path('shipping-method/', get_shipping_method,name='shipping-method'),
    path('error/', trigger_error,name='error'),



    path('all-review/<slug:slug>/', ProductReviewList.as_view(), name='product-reviews-list'),
    path('all-review/store/<slug:slug>/', StoreReviewList.as_view(), name='store-reviews-list'),
    
    path('mob/profile/nav',MobProfileNav.as_view(),name='mob-profile-nav'),


    path('autocomplete/search/',autocomplete,name='autocomplete-search'),
    path('about-us/',AboutUs.as_view(),name='about-us'),
    path('terms-and-condition/',TermsAndConditions.as_view(),name='terms-condition'),
    path('privacy-policy/',PrivacyPolicy.as_view(),name='privacy-policy'),


    path('get/area/list/',cityAreaList,name='get-city-area'),
    path('get/city/list/',cityList,name='get-city'),

    # path('sent-sms/',send_order_sms, name='send-sms')

]
