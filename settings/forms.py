from django import forms
from .models import *
from django.forms import formset_factory
from django.contrib.admin import widgets

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = '__all__'
        fields_required = ['outlet_name','store_address','contact_number','delivery_available_time','minimum_order_price']
        widgets = {
        'outlet_name': forms.TextInput(attrs=({'placeholder': 'Your outlet name (e.g : Cake977)','class': 'form-control'})),
        'outlet_type': forms.TextInput(attrs=({'placeholder': 'Your outlet type (e.g : Resturant, Dairy,etc)','class': 'form-control'})),
        'store_address': forms.TextInput(attrs=({'placeholder': 'Your outlet address','class': 'form-control'})),
        'contact_email': forms.TextInput(attrs=({'placeholder': 'Your contact email (e.g : info@gmail.com)','class': 'form-control','type':'email'})),
        'whatsapp_number': forms.NumberInput(attrs=({'placeholder': 'Your whatsapp number (e.g: 9779803622854)','class': 'form-control'})),
        'contact_number': forms.NumberInput(attrs=({'placeholder': 'Your contact number','class': 'form-control'})),
        'delivery_available_time': forms.TextInput(attrs=({'placeholder': 'Delivery avaialble from (e.g : 10AM - 5PM)','class': 'form-control'})),
        'minimum_order_price': forms.NumberInput(attrs=({'placeholder': 'Minimum price to be ordered (e.g: 2000)','class': 'form-control'})),
        'brand_color': forms.TextInput(attrs=({'placeholder': 'Select brand color (Primary)','class': 'form-control','id':'basic-colorpicker'})),
        'delivery_charge': forms.NumberInput(attrs=({'placeholder': 'Delivery Charge (e.g. 1000)','class': 'form-control'})),
        'nepxpress_username': forms.TextInput(attrs=({'placeholder': 'Nepexpress Username (key)','class': 'form-control'})),
        'nepxpress_password': forms.TextInput(attrs=({'placeholder': 'Nepexpress Username (password)','class': 'form-control'})),
        'currency': forms.Select(attrs={'class': 'form-control'}),
        'banner_redirect_url': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Redirect url for banner image'}),
        'banner_top_message': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Redirect url for banner image'}),
        'banner_top_message_redirect': forms.TextInput(attrs={'class': 'form-control','placeholder': 'Redirect url for banner image'}),
        'script_tags': forms.Textarea(attrs={'class': 'form-control','placeholder': 'Enter meta tags script here.'}),

        }
        error_messages = {
        'outlet_name': {'required': 'Please enter product  name.'},

         }




# class LocationForm(forms.ModelForm):
#     class Meta:
#         model = Location
#         fields = '__all__'

#         widgets = {
#         'name': forms.TextInput(attrs=({'placeholder': 'Enter locations Name','class': 'form-control'})),
#         'delivery_charge': forms.NumberInput(attrs=({'placeholder': 'Enter Delivery Charge','class': 'form-control'})),
#         }
#         error_messages = {
#         'name': {'required': 'Please enter locations  name.'},
#         'delivery_charge': {'required': 'Please enter delivery charge  name.'},



#     }



class OutletForm(forms.ModelForm):
    class Meta:
        model = OutletBranch
        fields = '__all__'

        widgets = {
        'branch_name': forms.TextInput(attrs=({'placeholder': 'Enter outlet branch Name','class': 'form-control'})),

        }
        error_messages = {
        'name': {'required': 'Please enter locations  name.'},



    }


