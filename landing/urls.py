from django.urls import path
from .views import *
from django.views.generic import TemplateView

app_name = 'landing'

urlpatterns = [
    path('section-one/<slug:slug>/', landing_section_one, name='section-one'),
    path('get/location/list/',locationList,name='read-location-list'),

    path('landing/category/list/<slug:slug>/',categoryList,name="category-list"),
	path('landing/category/delete/<int:pk>/<slug:slug>/',categoryDelete,name="category-delete"),
	path('landing/category-create/<slug:slug>/',categoryCreate,name="category-create"),
	path('landing/category/update/<int:pk>/<slug:slug>/',categoryUpdate,name="category-update"),
	path('landing/category/bulk/delete/<slug:slug>/',deleteCategoryBulk,name='category-bulk-delete'),
	path('landing/ajax/category/status/update/<slug:slug>/',categoryActiveUpdate,name='category-status'),

	path('landing/product/list/<slug:slug>/',productList,name="product-list"),
	path('landing/product/delete/<int:pk>/<slug:slug>/',productDelete,name="product-delete"),
	path('landing/product-create/<slug:slug>/',productCreate,name="product-create"),
	path('landing/ajax/product/update/<int:pk>/<slug:slug>/',productUpdate,name="product-update"),
	path('landing/product/bulk/delete/<slug:slug>/',deleteProductBulk,name='product-bulk-delete'),
	path('landing/ajax/product/status/update/<slug:slug>/',productActiveUpdate,name='product-status'),


	path('landing/store/list/<slug:slug>/',storeList,name="store-list"),
	path('landing/store/delete/<int:pk>/<slug:slug>/',deleteStore,name="store-delete"),
	path('landing/store-create/<slug:slug>/',storeCreate,name="store-create"),
	path('landing/ajax/store/update/<int:pk>/<slug:slug>/',updateStore,name="store-update"),
	path('landing/store/bulk/delete/<slug:slug>/',deleteStoreBulk,name='store-bulk-delete'),
	path('landing/ajax/store/status/update/<slug:slug>/',storeActiveUpdate,name='store-status'),


	path('landing/flavour/list/<slug:slug>/',flavourList,name="flavour-list"),
	path('landing/flavour/delete/<int:pk>/<slug:slug>/',flavourDelete,name="flavour-delete"),
	path('landing/flavour-create/<slug:slug>/',flavourCreate,name="flavour-create"),
	path('landing/flavour/update/<int:pk>/<slug:slug>/',flavourUpdate,name="flavour-update"),
	path('landing/flavour/bulk/delete/<slug:slug>/',deleteFlavourBulk,name='flavour-bulk-delete'),
	path('landing/ajax/flavour/status/update/<slug:slug>/',flavourActiveUpdate,name='flavour-status'),


	path('landing/banner/list/<slug:slug>/',bannerList,name="banner-list"),
	path('landing/banner/delete/<int:pk>/<slug:slug>/',bannerDelete,name="banner-delete"),
	path('landing/banner-create/<slug:slug>/',bannerCreate,name="banner-create"),
	path('landing/banner/update/<int:pk>/<slug:slug>/',bannerUpdate,name="banner-update"),
	path('landing/banner/bulk/delete/<slug:slug>/',deleteBannerBulk,name='banner-bulk-delete'),
	path('landing/ajax/banner/status/update/<slug:slug>/',bannerActiveUpdate,name='banner-status'),
]
