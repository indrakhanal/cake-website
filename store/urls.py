from django.urls import path
from django.views.generic import TemplateView
from .views import *
# from .views import *
app_name = 'store'

urlpatterns = [
	path('store/list',storeList,name='store-list'),
	path('store/create/',storeCreate,name='store-create'),
	path('store/delete/<int:pk>/', deleteStore, name='store-delete'),
	path('store/bulk/delete/',deleteStoreBulk,name='store-bulk-delete'),
	path('store/update/<int:pk>/', updateStore, name='store-update'),
	path('ajax/store/status/update/',storeAvailableStatus,name='store-available-status'),


	path('locations/',locationsList,name="locations-list"),
	path('locations/delete/<int:pk>/',locationsDelete,name="locations-delete"),
	path('ajax/locations/create/',locationsAjaxCreate,name="ajax-locations-create"),
	path('ajax/locations/update/<int:pk>/',locationsAjaxUpdate,name="ajax-locations-update"),
	path('locations/bulk/delete/',deleteLocationsBulk,name='locations-bulk-delete'),

	path('ajax/location/status/update/',locAvailableStatus,name='loc-available-status'),



	# path('sub-locations/<int:loc>',subLocationsList,name="sub-locations-list"),
	# path('sub-locations/delete/<int:loc>/<int:pk>/',subLocationsDelete,name="sub-locations-delete"),
	# path('ajax/sub-locations/create/<int:loc>/',subLocationsAjaxCreate,name="ajax-sub-locations-create"),
	# path('ajax/sub-locations/update/<int:loc>/<int:pk>/',subLocationsAjaxUpdate,name="ajax-sub-locations-update"),
	# path('sub-locations/bulk/delete/<int:loc>/',deletesubLocationsBulk,name='sub-locations-bulk-delete'),

	
]
