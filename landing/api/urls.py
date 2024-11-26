from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('get-section-first',ListRetrieveSectionOneView,basename='get-section-first')
router.register('post-section-first',CreateUpdateDestroySectionOneView,basename='post-section-first')
router.register('get-landing-categories',ListRetrieveLandingCategoriesView,basename='get-landing-categories')
router.register('post-landing-categories',CreateUpdateDestroyLandingCategoriesView,basename='post-landing-categories')
router.register('get-best-seller-products',ListRetrieveBestSellersSectionView,basename='get-landing-categories')
router.register('post-best-seller-products',CreateUpdateDestroyBestSellersSectionView,basename='post-best-seller-products')
router.register('get-banner',ListRetrieveLandingFullBannerView,basename='get-banner')
router.register('post-banner',CreateUpdateDestroyLandingFullBannerView,basename='post-banner')
router.register('get-popular-flavour',ListRetrievePopularFlavourSectionView,basename='get-popular-flavour')
router.register('post-popular-flavour',CreateUpdateDestroyPopularFlavourSectionView,basename='post-popular-flavour')
router.register('get-explore-store',ListRetrieveExploreStoreView,basename='get-explore-store')
router.register('post-explore-store',CreateUpdateDestroyExploreStoreView,basename='post-explore-store')
# router.register('get-put-delete-email',RetrieveUpdateDestroyContactSubscriptionEmailView,basename='rud-email')

urlpatterns = [

path('',include(router.urls)),

]
