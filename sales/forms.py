from django import forms
from .models import *
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.admin import widgets     


class AssignDeliveryForm(forms.ModelForm):
	def __init__(self,*args,**kwargs):
		super (AssignDeliveryForm,self ).__init__(*args,**kwargs) # populates the post
		self.fields['user'].queryset = User.objects.filter(profile__is_delivery_person=True)
		# self.fields['pickup_time'].widget = widgets.AdminSplitDateTime()

        
	class Meta:
		model = OrderDelivery
		fields = '__all__'
		exclude=['order','pickup_time','store']
		widgets = {
		'user': forms.Select(attrs=({'placeholder': 'Select delivery boy','class': 'form-control'})),
		'factory': forms.Select(attrs=({'placeholder': 'Select Factory','class': 'form-control'})),

}


from django.forms import formset_factory
class OrderForm(forms.ModelForm):    
	class Meta:
		model = Order
		fields = '__all__'

OrderFormSet = formset_factory(OrderForm,extra=1)

class OrderItemForm(forms.ModelForm):
	
	class Meta:
		model=OrderItem
		fields=['product','quantity','is_sugerless','is_eggless',]
		widgets = {
			'product': forms.Select(attrs=({'placeholder': 'Select product','class': 'form-control select2'})),

	}
OrderitemFormSet = formset_factory(OrderItemForm,extra=1)

class DeliveryAddressForm(forms.ModelForm):
	class Meta:
		model=DeliveryAddress
		fields='__all__'

		widgets={'sender_fullname': forms.TextInput(attrs={'placeholder': 'Please enter full name.'}),
		'sender_email': forms.TextInput(attrs={'placeholder': 'Please enter email.'}),
		'contact_number': forms.TextInput(attrs={'placeholder': 'Please enter Contact number.'}),
		'sender_address': forms.TextInput(attrs={'placeholder': 'Please enter address.'}),
		'i_am_receiver': forms.CheckboxInput(attrs={'placeholder': 'Sender full name.','class':'material-control-indicator'}),
		'receiver_fullname': forms.TextInput(attrs={'placeholder': 'Enter Receiver Name.'}),
		'receiver_email': forms.TextInput(attrs={'placeholder': 'Enter Receiver Email.'}),
		'receiver_delivery_address': forms.TextInput(attrs={'placeholder': 'Enter Receiver Address.'}),
		'receiver_landmark': forms.TextInput(attrs={'placeholder': 'Enter Receiver Landmark.','required':'required'}),
		'receiver_city': forms.TextInput(attrs={'placeholder': 'Enter Receiver city.'}),
		'receiver_area': forms.TextInput(attrs={'placeholder': 'Enter Receiver area.'}),
		'receiver_address_type': forms.RadioSelect(attrs={'placeholder': 'Select Receiver address type.'}),
		'receiver_contact_number1': forms.NumberInput(attrs={'placeholder': 'Enter Receiver phone Number.'}),
		'receiver_contact_number2': forms.NumberInput(attrs={'placeholder': 'Enter Receiver alternative phone number.'}),
		'occasion': forms.Select(attrs={'placeholder': 'Select occasion.'}),
		'social_media_handler': forms.TextInput(attrs={'placeholder': 'Enter Social media handler.'}),
		# 'source': forms.Select(attrs={'placeholder': 'Enter Social media handler.'}),

		}
		labels = {
        "sender_fullname": "Name",
        "sender_email": "Email",
        "contact_number": "Phone Number",
        "sender_address": "Address",
        "i_am_receiver": "Is Receiver",
        "receiver_fullname":"Name",
        "receiver_email": "Email",
        "receiver_delivery_address": "Address",
        "receiver_landmark": "Landmark",
        "receiver_address_type": "Delivery Address Type",
        "receiver_contact_number1": "Phone Number",
        "receiver_contact_number2": "Alt Phone Number",
    	}


from catalog.models import ProductAddons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column

class CustomOrderForm(forms.Form):
	name_choice = (('Basic Cake', 'Basic Cake'),
				('Fondant Cake', 'Fondant Cake'),
				('Basic Fondant Cake', 'Basic Fondant Cake'),
				('Jar Cake', 'Jar Cake'),
				('Mini Cake', 'Mini Cake'),
				('Bento Cake', 'Bento Cake'),
				('Pastry - Round', 'Pastry - Round'),
				('Brownie', 'Brownie'),
				('Doughnut','Doughnut'),
				('Muffin', 'Muffin'),
				('Cupcake', 'Cupcake'),
				('Cookies', 'Cookies'),
				('Pastry - Rectangle', 'Pastry - Rectangle'))
	flavour_choices = (('Black Forest', 'Black Forest'),
			('Blueberry','Blueberry'),
			('Brownie', 'Brownie'),
			('Butterscotch', 'Butterscotch'),
			('Choco Butter', 'Choco Butter'),
			('Choco Truffle', 'Choco Truffle'),
			('Choco Vanilla', 'Choco Vanilla'),
			('Chocolate', 'Chocolate'),
			('Coconut', 'Coconut'),
			('Coffee', 'Coffee'),
			('Mango', 'Mango'),
			('Mocha','Mocha'),
			('Oreo', 'Oreo'),
			('Pineapple', 'Pineapple'),
			('Red velvet', 'Red velvet'),
			('Strawberry', 'Strawberry'),
			('Tiramisu', 'Tiramisu'),
			('Truffle', 'Truffle'),
			('Vanilla', 'Vanilla'),
			('White Forest', 'White Forest'),
		    )
	name = forms.ChoiceField(widget=forms.Select,choices=name_choice, required=True)
	weight = forms.FloatField(initial=0.5,widget = forms.NumberInput(attrs = {'required':'required'}))
	flavour = forms.ChoiceField(widget=forms.Select,choices=flavour_choices, required=True)
	price = forms.FloatField(widget=forms.TextInput(attrs={'placeholder': 'Enter price.','required':'required'}))
	addons = forms.ModelMultipleChoiceField(widget=forms.SelectMultiple,
        queryset=ProductAddons.objects.filter(is_active = True),
        required=False)
	is_eggless =forms.BooleanField(initial=False, required=False)
	is_sugarless =forms.BooleanField(initial=False, required=False)
	image = forms.FileField(required = False)
	image2 = forms.FileField(required = False)
	image3 = forms.FileField(required = False)
	image4 = forms.FileField(required = False)
	message = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter message.'}))
	
	import secrets
	def clean_name(self):
		name=self.cleaned_data.get('name')
		if Product.objects.filter(name=name).exists():
			return name+'--'+str(secrets.token_hex(3))
			# raise forms.ValidationError("Product name must be unique.")
		return name
CustomOrderFormSet = formset_factory(CustomOrderForm,extra=1)


class PaymentMethodForm(forms.Form):
	methods = (('COD', 'COD'),
		('KHALTI', 'KHALTI'),
        ('ESEWA', 'ESEWA'),
        ('IME', 'IME'),
        ('CARD', 'CARD'),
        ('BANK', 'BANK'),
        ('CREDIT', 'CREDIT'),
        ('FONEPAY', 'FONEPAY'),
        ('COD FONEPAY', 'COD FONEPAY'),
        ('COD ESEWA', 'COD ESEWA'),
        ('COD KHALTI', 'COD KHALTI'),
                        
		)
	payment_method = forms.ChoiceField(widget=forms.Select,
        choices=methods,
        required=True)

	vendor = forms.ModelChoiceField(widget=forms.Select,
        queryset=Vendor.objects.all(),
        required=False)

	remarks = forms.CharField(widget=forms.Textarea, required = False)



class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = '__all__'

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter vendor Name','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter vendor  name.'},  
    }

class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = '__all__'

        widgets = {
        'name': forms.TextInput(attrs=({'placeholder': 'Enter vendor Name','class': 'form-control'})),
        'address': forms.TextInput(attrs=({'placeholder': 'Enter vendor Address','class': 'form-control'})),
        }
        error_messages = {
        'name': {'required': 'Please enter vendor  name.'}, 
        'address': {'required': 'Please enter vendor  address.'},  
    }


class OrderAlertForm(forms.ModelForm):
	class Meta:
		model = OrderAlert
		# exclude=['start_time','end_time']
		fields = '__all__'

		widgets = {
        'start_time': forms.TimeInput(attrs=({'class': 'form-control','type':'time'})),
        'end_time': forms.TimeInput(attrs=({'class': 'form-control','type':'time'})),
        'threshold': forms.NumberInput(attrs=({'class': 'form-control'})),
        }

