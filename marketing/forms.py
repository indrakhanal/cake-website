from django import forms
from .models import *
class CouponForm(forms.ModelForm):
    class Meta:
        model = CartCoupon
        fields = '__all__'
        exclude=['time_limit','is_active']

        widgets = {
        'coupon_type': forms.Select(attrs=({'placeholder': 'Choose coupon type.','class': 'form-control'})),
        'value': forms.NumberInput(attrs=({'placeholder': 'Enter discount price / rate.','class': 'form-control','min':"0"})),
        'coupon_number': forms.TextInput(attrs=({'placeholder': 'Enter coupon number.','class': 'form-control','min':"0"})),
        'total_user_limit': forms.NumberInput(attrs=({'placeholder': 'Total user limit.','class': 'form-control','rows':3})),
        'per_user_limit': forms.NumberInput(attrs=({'placeholder': 'Per user limit.','class': 'form-control'})),
        'min_cart_price': forms.NumberInput(attrs=({'placeholder': 'Minimum price','class': 'form-control','min':"0"})),
        'max_cart_price': forms.NumberInput(attrs=({'placeholder': 'Maximum price','class': 'form-control','min':"0"})),
        'store': forms.Select(attrs=({ 'placeholder': 'Select Store','class': 'form-control'})),
        'category': forms.SelectMultiple(attrs=({ 'placeholder': 'Select Store','class': 'form-control'})),
        'product': forms.SelectMultiple(attrs=({ 'placeholder': 'Select Store','class': 'form-control'})),
        }
        error_messages = {
        'coupon_type': {'required': 'Please enter coupon type.'},
        'value': {'required': 'Please enter  discount price.'},
        'coupon_number': {'required': 'Please enter  coupon number.'},
        'total_user_limit': {'required': 'Please enter  total user limit.'},
        'per_user_limit': {'required': 'Please enter per user limit.'},
        'min_cart_price': {'required': 'Please enter min cart price.'},
        'max_cart_price': {'required': 'Please enter max  cart price.'},
 
    }
    