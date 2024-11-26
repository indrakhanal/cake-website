from django.urls import path, include
from rest_framework import routers
from .views import *


router = routers.DefaultRouter()
router.register('get-location',ListRetrieveLocationView)
router.register('post-location',CreateUpdateDestroyLocationView)
# router.register('get-store',ListRetrieveStoreView)
router.register('post-store',CreateUpdateDestroyStoreView)
router.register('get-store-review',ListRetrieveStoreReviewView)
# router.register('post-store-review',CreateUpdateDestroyStoreReviewView)
router.register('delete-store-review',DestroyStoreReviewView)


urlpatterns = [

path('',include(router.urls)),
path('post-store-review/<int:pk>/',CreateUpdateStoreReviewView.as_view()),
path('list-store/<location>/<filter_value>/',ListStoreView.as_view({'get':'list'})),
path('read-store/<location>/<store_slug>/',RetrieveStoreView.as_view()),
# path('get-products-through-location/<slug>/',RetrieveLocationView.as_view())


]
