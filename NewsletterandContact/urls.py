from django.urls import path
from django.views.generic import TemplateView
from .views import *
# from .views import *
app_name = 'NewsletterandContact'

urlpatterns = [
path('subscription/email/',emailList,name="sub-emails"),
path('email/delete/<int:pk>/',emailDelete,name="email-delete"),
path('email/bulk/delete/',deleteEmailBulk,name='email-bulk-delete'),


path('contact/message/',contactList,name="contact-message"),
path('contact/delete/<int:pk>/',contactDelete,name="contact-delete"),
path('contact/bulk/delete/',deleteContactBulk,name='contact-bulk-delete'),


]
