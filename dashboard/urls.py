from django.urls import path
# from .views import *
from django.views.generic import TemplateView
from .views import *
app_name = 'dashboard'

urlpatterns = [
path('',AdminDashboard.as_view(),name="admin-dashboard"),
path('customers/',get_all_customers,name="customers"),


]
