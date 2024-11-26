from django import forms
from smarttech_payment_api.models import *

class KhaltiCredentialForm(forms.ModelForm):
    class Meta:
        model = KhaltiCredential
        fields = '__all__'

        widgets = {
        'public_key': forms.TextInput(attrs=({'placeholder': 'Enter public key','class': 'form-control'})),
        'secret_key': forms.TextInput(attrs=({'placeholder': 'Enter secret key','class': 'form-control'})),
        }
        

class EsewaCredentialForm(forms.ModelForm):
    class Meta:
        model = EsewaCredential
        fields = '__all__'

        widgets = {
        'service_code': forms.TextInput(attrs=({'placeholder': 'Enter service code','class': 'form-control'})),
        }

