from django.db import models
from catalog.models import Category, Product, Store, Flavour
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from store.models import Location 



class SectionOne(models.Model):
    location=models.ForeignKey(Location,related_name='section_one',on_delete=models.CASCADE)
    image_1 = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_1_thumbnail = ImageSpecField(source='image_1',
                                     processors=[ResizeToFill(1200, 800)],
                                     format='JPEG',
                                     options={'quality': 100})
  
    redirect_url_1 = models.CharField(max_length=800)
    image_2 = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_2_thumbnail = ImageSpecField(source='image_2',
                                     processors=[ResizeToFill(600, 478)],
                                     format='JPEG',
                                     options={'quality': 100})
    redirect_url_2 = models.CharField(max_length=800)
    image_3 = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_3_thumbnail = ImageSpecField(source='image_3',
                                     processors=[ResizeToFill(600, 478)],
                                     format='JPEG',
                                     options={'quality': 100})
    redirect_url_3 = models.CharField(max_length=800)
    image_4 = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_4_thumbnail = ImageSpecField(source='image_4',
                                     processors=[ResizeToFill(600, 478)],
                                     format='JPEG',
                                     options={'quality': 100})
    redirect_url_4 = models.CharField(max_length=800)
    image_5 = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_5_thumbnail = ImageSpecField(source='image_5',
                                     processors=[ResizeToFill(600, 478)],
                                     format='JPEG',
                                     options={'quality': 100})
    redirect_url_5 = models.CharField(max_length=800)

    class Meta:
        verbose_name_plural = 'SectionOne'
        ordering = ('-id',)
    
    
    @classmethod
    def create_section_1(cls, request, form,location):
        image_1 = request.FILES.get('image_1', None)
        image_2 = request.FILES.get('image_2', None)
        image_3 = request.FILES.get('image_3', None)
        image_4 = request.FILES.get('image_4', None)
        image_5 = request.FILES.get('image_5', None)

        if form.is_valid():
            form_obj = form.save(commit=False)
            form_obj.image_1 = image_1
            form_obj.image_2 = image_2
            form_obj.image_3 = image_3
            form_obj.image_4 = image_4
            form_obj.image_5 = image_5
            form_obj.location=location
            form_obj.save()
            return "Created Successfully"

    @classmethod
    def update_section_1(cls, request, form,location):
        image_1 = request.FILES.get('image_1', None)
        image_2 = request.FILES.get('image_2', None)
        image_3 = request.FILES.get('image_3', None)
        image_4 = request.FILES.get('image_4', None)
        image_5 = request.FILES.get('image_5', None)

        image_1_clear = request.POST.get('image_1-clear', None)
        image_2_clear = request.POST.get('image_2-clear', None)
        image_3_clear = request.POST.get('image_3-clear', None)
        image_4_clear = request.POST.get('image_4-clear', None)
        image_5_clear = request.POST.get('image_5-clear', None)

        if form.is_valid():
            form_obj = form.save(commit=False)

            if image_1_clear:
                form_obj.image_1 = None
            if image_1:
                form_obj.image_1 = image_1

            if image_2_clear:
                form_obj.image_2 = None
            if image_2:
                form_obj.image_2 = image_2

            if image_3_clear:
                form_obj.image_3 = None
            if image_3:
                form_obj.image_3 = image_3

            if image_4_clear:
                form_obj.image_4 = None
            if image_4:
                form_obj.image_4 = image_4

            if image_5_clear:
                form_obj.image_5 = None
            if image_5:
                form_obj.image_5 = image_5
            form_obj.location=location
            form_obj.save()
            return "Updated Successfully"

    @classmethod
    def get_section_one_items(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(location=location).last()


class LandingCategories(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location=models.ForeignKey(Location,related_name='landing_categories',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/landing/categories/', blank=True, null=True, max_length=700)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)

   

    @classmethod
    def get_landing_categories(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(is_active=True,location=location).order_by('display_order')[:6]
    
    @classmethod
    def updateActiveStatus(cls,location,val,item):
        if val == 'True':
            is_available=True
        if val == 'False':
            is_available=False
        cls.objects.filter(id=item,location__slug=location.slug).update(is_active=is_available)

class BestSellersSection(models.Model):
    location=models.ForeignKey(Location,related_name='best_seller_section',on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)
    
    
    
    @classmethod
    def get_best_seller_products(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(is_active=True,location=location).order_by('display_order')[:8]
    
    @classmethod
    def updateActiveStatus(cls,location,val,item):
        if val == 'True':
            is_available=True
        if val == 'False':
            is_available=False
        cls.objects.filter(id=item,location__slug=location.slug).update(is_active=is_available)

class LandingFullBanner(models.Model):
    location=models.ForeignKey(Location,related_name='full_banner',on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(2880, 824)],
                                     format='JPEG',
                                     options={'quality': 100})
    redirect_url = models.CharField(max_length=800)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)

    

    @classmethod
    def get_section_four_banner_items(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(is_active=True,location=location).order_by('display_order')[:4]

    @classmethod
    def updateActiveStatus(cls,location,val,item):
        if val == 'True':
            is_available=True
        if val == 'False':
            is_available=False
        cls.objects.filter(id=item,location__slug=location).update(is_active=is_available)

class PopularFlavourSection(models.Model):
    location=models.ForeignKey(Location,related_name='popular_flavour',on_delete=models.CASCADE)
    flavour = models.ForeignKey(Flavour, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='images/landing', blank=True, null=True, max_length=700)
    image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(508, 508)],
                                     format='JPEG',
                                     options={'quality': 100})
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)

    

    @classmethod
    def get_popular_flavours(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(is_active=True,location=location).order_by('display_order')[:8]

    @classmethod
    def updateActiveStatus(cls,location,val,item):
        if val == 'True':
            is_available=True
        if val == 'False':
            is_available=False
        cls.objects.filter(id=item,location__slug=location.slug).update(is_active=is_available)

class ExploreStore(models.Model):
    location=models.ForeignKey(Location,related_name='explore_stores',on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)

   
    
    @classmethod
    def get_store(cls,request):
        location = Location.get_store_location_obj(request)
        return cls.objects.filter(is_active=True,location=location).order_by('display_order')[:12]
    
    @classmethod
    def updateActiveStatus(cls,location,val,item):
        if val == 'True':
            is_available=True
        if val == 'False':
            is_available=False
        cls.objects.filter(id=item,location__slug=location.slug).update(is_active=is_available)