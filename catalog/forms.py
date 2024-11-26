from django import forms
from .models import *
from ckeditor_uploader.widgets import  CKEditorUploadingWidget


class FileUploadForm(forms.Form):
    file=forms.FileField()
    
class TagForm(forms.ModelForm):
    class Meta:
        model = Tags
        fields = '__all__'

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter tags Name','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter tags  name.'},
        
        
        
    }

    

class FlavourForm(forms.ModelForm):
    class Meta:
        model = Flavour
        fields = '__all__'
        exclude=['slug']
        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter flavour Name','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter flavour name.'},
        
        
        
    }

class AttributeForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = '__all__'

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter attribute Name','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter attribute  name.'},
        
        
        
    }

class ProductAttributeValueForm(forms.ModelForm):
    class Meta:
        model = Attribute
        fields = '__all__'


class AddonForm(forms.ModelForm):
    class Meta:
        model = ProductAddons
        fields = '__all__'
        

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter addon Name','class': 'form-control'})),
        'price': forms.NumberInput(attrs=({'placeholder': 'Enter  Price','class': 'form-control'})),
        'types': forms.Select(attrs=({'placeholder': 'Select  type','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter addon  name.'},
        'price': {'required': 'Please enter addon  price.'},
        
        
    }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
    
        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter Category Name','class': 'form-control'})),
        'slug': forms.TextInput(attrs=({'placeholder': 'Enter Category Slug','class': 'form-control'})),
        'description': forms.Textarea(attrs=({'placeholder': 'Enter Category Description','class': 'form-control','rows':3})),
        'parent': forms.Select(attrs=({'placeholder': ' Select Main Category','class': 'form-control select2'})),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Display Order','class': 'form-control'})),
        'image': forms.FileInput(attrs=({'class': 'dropify','data-height':'200', 'accept':'image/*'})),
        
        }
        error_messages = {
        'name': {'required': 'Please enter category  name.'},
        
        
    }
    

# from django.contrib.admin import widgets

class ProductForm(forms.ModelForm):
    def __init__(self,*args,**kwargs):
        super (ProductForm,self ).__init__(*args,**kwargs) # populates the post
        self.fields['addons'].queryset = ProductAddons.objects.filter(is_active=True)
    class Meta:
        model = Product
        fields = '__all__'
        exclude=['store']
        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter Product Name','class': 'form-control','autocomplete':'off'})),
        'slug': forms.TextInput(attrs=({'placeholder': 'Enter Product slug','class': 'form-control','autocomplete':'off'})),
        'description': forms.TextInput(attrs=({'placeholder': 'Short Product Summary','class': 'form-control','rows':1})),
        'long_description': forms.CharField(widget=CKEditorUploadingWidget()),
        'delivery_information': forms.CharField(widget=CKEditorUploadingWidget()),
        'instruction': forms.CharField(widget=CKEditorUploadingWidget()),
        'display_order': forms.NumberInput(attrs=({'placeholder': 'Display Order','class': 'form-control','min':"0"})),
        'tags': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'category': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'shipping_method': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'related_products': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'addons': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'flavour': forms.SelectMultiple(attrs=({'class':'form-control select2-multiple', 'data-toggle':'select2', 'multiple':'multiple',
                'data-placeholder':'Choose ...'})),
        'note': forms.TextInput(attrs=({'placeholder': 'Additional information for customer','class': 'form-control'})),
        'min_order_time': forms.NumberInput(attrs=({'placeholder': 'Minimum Order Time','class': 'form-control','min':"1"})),
        
        }
        error_messages = {
        'name': {'required': 'Please enter product  name.'},
        'image': {'required': 'Please enter  product image.'},
    }
    
class ProductVarientForm(forms.ModelForm):
    attribute_name_1 = forms.CharField(required=False)
    attribute_value_1 = forms.CharField(required=False)
    attribute_name_2 = forms.CharField(required=False)
    attribute_value_2 = forms.CharField(required=False)

    class Meta:
        model = ProductVarient
        fields = '__all__'
        exclude=['slug','product','varient_name']

        widgets = {
        'varient_name': forms.TextInput(attrs=({'placeholder': 'Enter Product Name','class': 'form-control','name':'varient_name'})),
        'old_price': forms.NumberInput(attrs=({'placeholder': 'Enter Product Old Price','class': 'form-control','min':"0"})),
        'price': forms.NumberInput(attrs=({'placeholder': 'Enter Product New Price','class': 'form-control'})),
        'cost_price': forms.NumberInput(attrs=({'placeholder': 'Enter Product Cost Price','class': 'form-control'})),
        
        'product_code': forms.TextInput(attrs=({'placeholder': 'Enter Product Code (SKU)','class': 'form-control'})),
        'display_order_varient': forms.NumberInput(attrs=({'placeholder': 'Display Order','class': 'form-control','min':"0"})),
        'quantity': forms.NumberInput(attrs=({'placeholder': 'Quantity','class': 'form-control','min':"0"})),
        }
        error_messages = {
        'varient_name': {'required': 'Please enter product  name.'},
        'price': {'required': 'Please enter  product price.'},
        'image': {'required': 'Please enter  product image.'},
        'product_code': {'required': 'Please enter  product code.'},
        
    

        
    }