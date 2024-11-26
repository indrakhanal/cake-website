from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register([Order,DeliveryAddress,OrderItem,DeliveryNepxpress,Cart,CartItem,AddonItem,OrderDelivery,AddonOrderItem,OrderAlert,OrderAssignedToVendor])