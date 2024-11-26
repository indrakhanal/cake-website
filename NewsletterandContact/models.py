from django.db import models as m
from django.core.validators import RegexValidator

# Create your models here.
class SubscriptionEmail(m.Model):
	email=m.EmailField(unique=True)

	def __str__(self):
		return self.email


class ContactMessage(m.Model):
	first_name=m.CharField(max_length=20)
	last_name=m.CharField(max_length=20)
	# phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	contact_number=m.CharField(max_length=11)
	message=m.TextField(max_length=500)

	def __str__(self):
		return self.contact_number