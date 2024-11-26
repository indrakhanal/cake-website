from .models import *
from django import forms

class StoreForm(forms.ModelForm):
    class Meta:
        model = Store
        fields = '__all__'
        exclude=['slug',]

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter store Name','class': 'form-control'})),
        'contact_number': forms.TextInput(attrs=({'placeholder': 'Enter contact number','class': 'form-control'})),
        'store_location1': forms.TextInput(attrs=({'placeholder': 'Enter store location','class': 'form-control'})),
        'eggless_price': forms.TextInput(attrs=({'placeholder': 'Enter eggless price per pound','class': 'form-control'})),
        'sugar_less_price': forms.TextInput(attrs=({'placeholder': 'Enter sugarless price per pound.','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter store  name.'},
        'name': {'required': 'Please enter contact number.'},
        'eggless_price': {'required': 'Please enter eggless  price per pound.'},
        'sugar_less_price': {'required': 'Please enter sugarless price per pound.'},
        
        
        
    }


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = '__all__'
        exclude=['slug',]

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter location Name','class': 'form-control'})),
        'parent': forms.Select(attrs=({'placeholder': 'Select Parent','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter location  name.'},
        
        
        
    }

# class SubLocationForm(forms.ModelForm):
#     class Meta:
#         model = SubLocation
#         fields = '__all__'
        

#         widgets = {
#         'name': forms.TextInput(attrs=({'placeholder': 'Enter sub location Name','class': 'form-control'})),
#         'location': forms.Select(attrs=({'placeholder': 'Select parent location Name','class': 'form-control'})),
#         }
#         error_messages = {
#         'name': {'required': 'Please enter location  name.'},


        
        
        
#     }


class FactoryModelForm(forms.ModelForm):
    class Meta:
        model = Factories
        fields = '__all__'

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter vendor Name','class': 'form-control'})),
        'address': forms.TextInput(attrs=({'placeholder': 'Enter vendor Address','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter vendor  name.'}, 
        'address': {'required': 'Please enter vendor  address.'},  
    }




