from django.urls import path
# from .views import *
from django.views.generic import TemplateView
from .views import *
from .nepxpress import *

app_name = 'utility'

urlpatterns = [

    path('nepexpress-post/', post_nepexpress, name='nepexpress-post'),
    path('nepexpress-track/', track_order, name='nepexpress-track'),

]
