from sales.models import OrderDelivery
from django import forms
from django.contrib.auth import get_user_model
User = get_user_model()

class AssignDeliveryForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super(AssignDeliveryForm, self).__init__(*args, **kwargs)
		self.fields['user'].label = "Delivery Boy"
		self.fields['user'].queryset = User.objects.filter(profile__is_delivery_person=True)
    
	class Meta:
		model = OrderDelivery
		fields = '__all__'
		exclude = ['store','order',]

		widgets = {
		'user':forms.Select(attrs=({'type':'text','class': 'form-control'})),
		'factory':forms.Select(attrs=({'type':'text','class': 'form-control'})),
		'pickup_date': forms.TextInput(attrs=({'type':'date','class': 'form-control'})),
		'pickup_time': forms.TextInput(attrs=({'type':'time','class': 'form-control'})),
		'expected_delivery_time': forms.TextInput(attrs=({'type':'time','class': 'form-control'})),
		'remarks':forms.TextInput(attrs=({'type':'text','class': 'form-control'})),
		}
        