from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from catalog.models import *
from django.core.files.storage import FileSystemStorage
import os
from imagekit.models import ImageSpecField
from django.shortcuts import get_object_or_404

from imagekit.processors import ResizeToFill


class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name, max_length):
        from django.conf import settings

        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, max_length)


class Settings(models.Model):
    CURRIENCIES = (('Rs', 'Nepalese Rupee (Rs)'),
                   ('INR', 'Indian Rupee (INR)'),
                   ('$', 'US Dollor (USD)'),
                   ('€', 'Euro (€)'),
                   ('£', 'Pound (£)'),
                   ('AUD', 'Australian Dollor (AU.$)'),
                   ('CAD', 'Canadian Dollor (CA.$)'),
                   )

    outlet_name = models.CharField(max_length=100)
    outlet_type = models.CharField(max_length=250, blank=True, null=True)
    store_address = models.CharField(max_length=250)
    delivery_charge = models.FloatField(default=0,blank=True,null=True)
    contact_email = models.EmailField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=13, blank=True, null=True)
    contact_number = models.CharField(max_length=13)
    currency = models.CharField(max_length=100, choices=CURRIENCIES, default='Rs')
    delivery_available_time = models.CharField(max_length=150)
    minimum_order_price = models.FloatField(blank=True,null=True)
    brand_color = models.CharField(max_length=150, blank=True, null=True)
    banner_image = models.ImageField(upload_to='images/settings', blank=True, null=True, max_length=700)
    banner_image_2 = models.ImageField(upload_to='images/settings', blank=True, null=True, max_length=700)
    banner_image_3 = models.ImageField(upload_to='images/settings', blank=True, null=True, max_length=700)
    banner_thumbnail = ImageSpecField(source='banner_image',
                                      processors=[ResizeToFill(1349, 321)],
                                      format='JPEG',
                                      options={'quality': 95})
    all_resturant = ImageSpecField(source='aggregator_image',
                                   processors=[ResizeToFill(540, 360)],
                                   format='JPEG',
                                   options={'quality': 1000})
    outlet_logo = models.ImageField(upload_to='images/settings', blank=True, null=True, max_length=700)
    aggregator_image = models.ImageField(upload_to='images/settings', blank=True, null=True, max_length=700)
    all_resturant_outlet_logo = ImageSpecField(source='outlet_logo',
                                               processors=[ResizeToFill(200, 200)],
                                               format='JPEG',
                                               options={'quality': 95})
    apply_extra_charge = models.BooleanField(default=False)
    flat_delivery = models.BooleanField(default=False)
    is_conditional_delivery_charge = models.BooleanField(default=False)
    is_locations_delivery_charge = models.BooleanField(default=False)

    nepxpress_username = models.CharField(max_length=500, blank=True, null=True)
    nepxpress_password = models.CharField(max_length=500, blank=True, null=True)
    banner_top_message = models.CharField(max_length=500, blank=True, null=True)
    banner_top_message_redirect = models.CharField(max_length=500, blank=True, null=True)
    script_tags=models.TextField(blank=True,null=True)

    class Meta:
        verbose_name_plural = 'Settings'
        ordering = ('-id',)

    def save(self, *args, **kwargs):
        if self.__class__.objects.count():
            self.pk = self.__class__.objects.first().pk
        super().save(*args, **kwargs)


# class Location(models.Model):
#     name = models.CharField(max_length=50)
#     delivery_charge = models.FloatField()
#     is_active = models.BooleanField()

#     class Meta:
#         verbose_name_plural = 'Locations'
#         ordering = ('-id',)


class OutletBranch(models.Model):
    branch_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)


class ShippingMethod(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    shipping_time = models.ManyToManyField('ShippingTime', related_name='shipping_time')
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Shipping Methods'
        ordering = ('-id',)
    
    @classmethod
    def get_shipping_method(cls,product):
        if product.shipping_method.all():
            return product.shipping_method.all().order_by('display_order')
        else:
            return cls.objects.filter(is_active=True).order_by('display_order')

    @classmethod
    def create_shipping_method(cls, name, price, is_active=True,display_order=1):
        try:
            shipping_method = cls.objects.create(name=name, price=price, is_active=is_active,display_order=display_order)
            return shipping_method
        except Exception as e:
            print(e)

    @classmethod
    def update_shipping_method(cls, pk, name, price, is_active=True,display_order=1):
        try:
            shipping_method = cls.objects.filter(id=pk).update(name=name, price=price, is_active=is_active,display_order=display_order)
            return cls.objects.get(id=pk)
        except Exception as e:
            print(e)

    @classmethod
    def add_shipping_time(cls, obj, time):
        try:
            obj.shipping_time.add(time)
        except Exception as e:
            print(e)

    @classmethod
    def deleteShippingMethod(cls, pk):
        get_object_or_404(cls, pk=pk).delete()

    @classmethod
    def bulkDelete(cls, ids):
        for i in range(0, len(ids)):
            cls.objects.filter(id=ids[int(i)]).delete()

    @classmethod
    def updateActiveStatus(cls, val, item):
        if val == 'True':
            is_available = True
        if val == 'False':
            is_available = False
        cls.objects.filter(id=item).update(is_active=is_available)

    @property
    def get_all_shipping_time(self):
        return self.shipping_time.all().order_by('display_order')
    
    @classmethod
    def get_filtered_shipping_method(cls,selected_date,product):
        import json
        from django.core.serializers.json import DjangoJSONEncoder
        import datetime
        from datetime import timedelta 
        
        min_order_time = product.min_order_time + 5.75
        current_date = (datetime.datetime.now() + timedelta(hours=5.75)).date()
        current_time = (datetime.datetime.now() + timedelta(hours=min_order_time)).time()
        obj =[]
        shipping_methods = cls.get_shipping_method(product)

        if str(selected_date) == str(current_date):
            for item in shipping_methods:
                time = item.shipping_time.filter(time_to__gt=current_time).values('id', 'time_from', 'time_to').order_by('display_order')
                if time:
                    serialized_time = json.dumps(list(time), cls=DjangoJSONEncoder)
                    obj.append({'shipping_method':item.name,'price':item.price,'id':item.id,'time':serialized_time})
            return obj
        else:
            for item in shipping_methods:
                time = item.shipping_time.all().values('id', 'time_from', 'time_to').order_by('display_order')
                if time:
                    serialized_time = json.dumps(list(time), cls=DjangoJSONEncoder)
                    obj.append({'shipping_method':item.name,'price':item.price,'id':item.id,'time':serialized_time})
            return obj
    

class ShippingTime(models.Model):
    time_from = models.TimeField(auto_now=False, auto_now_add=False)
    time_to = models.TimeField(auto_now=False, auto_now_add=False)
    display_order = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return '{0}-{1}'.format(self.time_from, self.time_to)

    @classmethod
    def create_shipping_time(cls, time_from, time_to, is_active=True,display_order = 1):
        return cls.objects.create(time_from=time_from, time_to=time_to, is_active=is_active,display_order=display_order)
        
        

    class Meta:
        verbose_name_plural = 'Shipping Time'
        ordering = ('-id',)
