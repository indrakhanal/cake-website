from django.urls import path
from .views import *
from django.views.generic import TemplateView
app_name = 'settings'

urlpatterns = [
path('edit/',settingsCreate , name='create'),
path('',settingsView , name='settings-view'),


# path('locations/',locationsList,name="locations-list"),
# path('locations/delete/<int:pk>/',locationsDelete,name="locations-delete"),
# path('ajax/locations/create/',locationsAjaxCreate,name="ajax-locations-create"),
# path('ajax/locations/update/<int:pk>/',locationsAjaxUpdate,name="ajax-locations-update"),
# path('locations/bulk/delete/',deleteLocationsBulk,name='locations-bulk-delete'),



path('outlet/branch/',outletBranchList,name="outlet-branch-list"),
path('outlet/branch/delete/<int:pk>/',outletBranchDelete,name="outlet-branch-delete"),
path('ajax/outlet/branch/create/',outletBranchAjaxCreate,name="ajax-outlet-branch-create"),
path('ajax/outlet/branch/update/<int:pk>/',outletBranchAjaxUpdate,name="ajax-outlet-branch-update"),
path('outlet/branch/bulk/delete/',deleteOutletBranchBulk,name='outlet-branch-bulk-delete'),
path('shipping-method/',create_shipping_method,name='shipping-method'),
path('edit-shipping-method/<int:pk>/',edit_shipping_method,name="edit-shipping-method"),
path('shipping-method-list/',shippingMethodList,name="shipping-method-list"),
path('shipping-method-delete/<int:pk>/', deleteShippingMethod, name='shipping-method-delete'),
path('shipping-method-bulk-delete/',deleteShippingMethodBulk,name='shipping-method-bulk-delete'),
path('ajax/shipping-method/status/update/',shippingAvailableStatus,name='shipping-available-status'),

]

