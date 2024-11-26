from django import forms
from .models import *
from django.core.exceptions import ValidationError

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = '__all__'

        widgets = {
        'first_name': forms.TextInput(attrs=({'placeholder': 'First Name','class': 'form-control'})),
        'last_name': forms.TextInput(attrs=({'placeholder': 'Last Name','class': 'form-control'})),
        'contact_number': forms.NumberInput(attrs=({'placeholder': 'Phone Number','class': 'form-control'})),
        'message': forms.Textarea(attrs=({'placeholder': 'Message','class': 'form-control','rows':'4'})),
        }
        error_messages = {
        'first_name': {'required': 'Please enter first  name.'},
        'last_name': {'required': 'Please enter last  name.'},
        'contact_number': {'required': 'Please enter contact  number.'},
        'message': {'required': 'Please enter message.'},
     	}
    
    def clean_contact_number(self):
    	number=self.cleaned_data['contact_number']
    	
    	if len(number) <10 or len(number)>11:
    		raise ValidationError('Phone number must be 10 digit.')
    	return number

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = SubscriptionEmail
        fields = '__all__'

        widgets = {
        'email': forms.EmailInput(attrs=({'placeholder': 'Enter your Email address..'})),
        
        }
        error_messages = {
        'email': {'required': 'Email is required.'},
        
     	}