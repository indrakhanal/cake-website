from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register('list-categories',ListRetrieveCategoryView,basename='get-categories')
router.register('post-category',CreateUpdateDestroyCategoryView,basename='post-category')
# router.register('get-brand',ListRetrieveBrandView)
# router.register('post-brand',CreateUpdateDestroyBrandView)
router.register('get-tags',ListRetrieveTagsView)
router.register('post-tags',CreateUpdateDestroyTagsView)
router.register('get-flavour',ListRetrieveFlavourView)
router.register('post-flavour',CreateUpdateDestroyFlavourView)
router.register('get-attribute',ListRetrieveAttributeView)
router.register('post-attribute',CreateUpdateDestroyAttributeView)
router.register('get-attribute-value',ListRetrieveAttributeValueView)
router.register('post-attribute-value',CreateUpdateDestroyAttributeValueView)
router.register('get-product-addons',ListRetrieveProductAddonsView)
router.register('post-product-addons',CreateUpdateDestroyProductAddonsView)
router.register('get-products',ListRetrieveProductView)
router.register('post-products',CreateUpdateDestroyProductView)
router.register('get-product-varient',ListRetrieveProductVarientView)
router.register('post-product-varient',CreateUpdateDestroyProductVarientView)
router.register('get-product-review',ListRetrieveProductReviewView)

urlpatterns = [

path('',include(router.urls)),
# path('get-categories/<cate_slug>/<location>/<keyword>/',ListRetrieveCategoryView.as_view({'get':'list'})),
path('read-categories/<cate_slug>/<location>/<keyword>/',RetrieveCategoryProductView.as_view({'get':'retrieve'})),
path('post-product-review/<int:pk>/',CreateUpdateProductReviewView.as_view()),
path('delete-product-review/<int:pk>/',DestroyProductReviewView.as_view()),
# path('detail-categories/<category_slug>/<product_slug>/',RetrieveCategoryProductView.as_view()),
path('get-products-through-flavour/<int:pk>/<location>/',RetrieveProductsThroughFlavour.as_view()),
path('search-product/<keyword>/',ProductSearchView.as_view()),

]

