from django.db import models
from django.contrib.auth.models import User
from store.models import Store, Factories
class UserProfile(models.Model):
    ODOO_STATUS_TYPE = (('Success', 'Success'),
                      ('Failed', 'Failed'),
                      ('None', 'None'))

    user = models.OneToOneField(User,related_name='profile', on_delete=models.CASCADE,blank=True)
    phone_number = models.CharField(max_length=11, blank=True,null=True)
    is_delivery_person=models.BooleanField(default=False)
    is_dispatcher=models.BooleanField(default=False)
    is_vendor=models.BooleanField(default=False)
    is_production_manager = models.BooleanField(default=False)
    store=models.ForeignKey(Store,null=True,blank=True,related_name='store',on_delete=models.CASCADE)
    factory=models.ForeignKey(Factories,null=True,blank=True,related_name='factories',on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=ODOO_STATUS_TYPE, default="None")


class OdooTokenStore(models.Model):
    access_key = models.TextField(null=True, blank=True)
    partner_id = models.CharField(max_length=20, null=True, blank=True)
    session_key = models.TextField(null=True, blank=True)