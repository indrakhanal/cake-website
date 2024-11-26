from functools import wraps
from django.http import HttpResponseRedirect
from catalog.models import Product, Store
from store.models import Location as StoreLocation

def valid_product_location_only(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
   product = Product.objects.get(slug= kwargs['slug'])
   selected_location = StoreLocation.get_store_location_obj(request.request)
   product_location = Product.objects.filter(store__location=selected_location,id=product.id).exists()
   if product_location:
      return function(request, *args, **kwargs)
   else:
      return HttpResponseRedirect('/')

  return wrap

def valid_store_location_only(function):
  @wraps(function)
  def wrap(request, *args, **kwargs):
   store = Store.objects.get(slug= kwargs['slug'])
   selected_location = StoreLocation.get_store_location_obj(request.request)
   store_location = Store.objects.filter(location=selected_location,id=store.id).exists()
   if store_location:
      return function(request, *args, **kwargs)
   else:
      return HttpResponseRedirect('/')

  return wrap
     
        