from django import forms
from .models import *
from django.forms import formset_factory
from django.contrib.admin import widgets

class SectionOneForm(forms.ModelForm):
    class Meta:
        model = SectionOne
        fields = '__all__'
        exclude=['location']
        # fields_required = ['outlet_name','store_address','whatsapp_number','delivery_available_time','opening_days','minimum_order_price']
        widgets = {
        'redirect_url_1': forms.TextInput(attrs={'type':'url','class': 'form-control','placeholder': 'https://example.com','pattern':'https?://.*'}),
        'redirect_url_2': forms.TextInput(attrs={'type':'url','class': 'form-control','placeholder': 'https://example.com','pattern':'https?://.*'}),
        'redirect_url_3': forms.TextInput(attrs={'type':'url','class': 'form-control','placeholder': 'https://example.com','pattern':'https?://.*'}),
        'redirect_url_4': forms.TextInput(attrs={'type':'url','class': 'form-control','placeholder': 'https://example.com','pattern':'https?://.*'}),
        'redirect_url_5': forms.TextInput(attrs={'type':'url','class': 'form-control','placeholder': 'https://example.com','pattern':'https?://.*'}),
        'image_1': forms.TextInput(attrs={'type':'file','class':'dropify', 'data-height':'475','accept':'image/*','onchange':'image_upload("image_1-clear_id")'}),
        'image_2': forms.TextInput(attrs={'type':'file','class':'dropify', 'data-height':'165','accept':'image/*','onchange':'image_upload("image_2-clear_id")'}),
        'image_3': forms.TextInput(attrs={'type':'file','class':'dropify', 'data-height':'165','accept':'image/*','onchange':'image_upload("image_3-clear_id")'}),
        'image_4': forms.TextInput(attrs={'type':'file','class':'dropify', 'data-height':'165','accept':'image/*','onchange':'image_upload("image_4-clear_id")'}),
        'image_5': forms.TextInput(attrs={'type':'file','class':'dropify', 'data-height':'165','accept':'image/*','onchange':'image_upload("image_5-clear_id")'}),
       
        }
        error_messages = {
        'redirect_url_1': {'required': 'Please enter product  name.'},
     
         }


class LandingCategoriesForm(forms.ModelForm):
    class Meta:
        model = LandingCategories
        fields = '__all__'
        exclude=['location']

        widgets = {
        'category': forms.Select(attrs=({'placeholder': 'Choose category','class': 'form-control'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Enter Display order','class': 'form-control'})),
        }
        error_messages = {
        'category': {'required': 'Please select category.'},
        'display_order': {'required': 'Please enter display order.'},
        
        
        
    }

class BestSellersSectionForm(forms.ModelForm):
    class Meta:
        model = BestSellersSection
        fields = '__all__'
        exclude=['location']

        widgets = {
        'product': forms.Select(attrs=({'placeholder': 'Choose product','class': 'form-control'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Enter Display order','class': 'form-control'})),
        }
        error_messages = {
        'category': {'required': 'Please select product.'},
        'display_order': {'required': 'Please enter display order.'},
        
        
        
    }



class ExploreStoreForm(forms.ModelForm):
    class Meta:
        model = ExploreStore
        fields = '__all__'
        exclude=['location']


        widgets = {
        'store': forms.Select(attrs=({'placeholder': 'Choose store','class': 'form-control'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Enter Display order','class': 'form-control'})),
        }
        error_messages = {
        'category': {'required': 'Please select store.'},
        'display_order': {'required': 'Please enter display order.'},
        
        
        
    }


class PopularFlavourSectionForm(forms.ModelForm):
    class Meta:
        model = PopularFlavourSection
        fields = '__all__'
        exclude=['location']

        widgets = {
        'flavour': forms.Select(attrs=({'placeholder': 'Choose flavour','class': 'form-control'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Enter Display order','class': 'form-control'})),
        }
        error_messages = {
        'flavour': {'required': 'Please select flavour.'},
        'display_order': {'required': 'Please enter display order.'},
        
        
        
    }


class LandingFullBannerForm(forms.ModelForm):
    class Meta:
        model = LandingFullBanner
        fields = '__all__'
        exclude=['image','location']

        widgets = { 
        
        'redirect_url': forms.TextInput(attrs=({'placeholder': 'Enter redirect url','class': 'form-control'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Enter Display order','class': 'form-control'})),
        }
        error_messages = {
        'redirect_url': {'required': 'Please enter redirect url.'},
        'display_order': {'required': 'Please enter display order.'},
    
    }

