from django.db import models
from catalog.utils import get_unique_slug
from django.urls import reverse
from django.conf import settings
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from mptt.models import MPTTModel, TreeForeignKey




class Location(MPTTModel):
    name = models.CharField(max_length=100)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active=models.BooleanField(default=True)
    slug = models.SlugField(max_length=100, unique=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        self.name = self.name.title()
        super().save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return self.name
    
    class MPTTMeta:
        order_insertion_by = ['name']

    def get_absolute_url(self):
        return reverse('client:location-products')
    
    @classmethod
    def get_store_location_obj(cls,request):
        if 'location_id' in request.session:
            try:
                return cls.objects.get(id=int(request.session['location_id']))
            except:
                del request.session['location_id']
                return None
        else:
            return cls.objects.first()

    @classmethod
    def store_location_id_in_session(cls,request,location_id):
        cls.remove_cart_item(request)
        try:
            request.session['location_id'] = location_id
        except:
            print("Unable to store location id in session")
    
    @classmethod
    def remove_cart_item(cls,request):
        from sales.models import CartItem
        try:
            if request.user.is_authenticated:
                CartItem.objects.filter(cart__user=request.user).all().delete()
            else:
                request.session.clear()
                
        except:
            print("Unable to delete location id from session")


# class SubLocation(models.Model):
#     name = models.CharField(max_length=30)
#     location=models.ForeignKey(Location,related_name='sub_location',null=True,blank=True, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.name

class Store(models.Model):
    name = models.CharField(max_length=30, unique=True)
    slug = models.SlugField(max_length=30, unique=True)
    contact_number=models.CharField(max_length=12)
    store_location1=models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/store/', blank=True, null=True)
    image_thumbnail_150X150 = ImageSpecField(source='image',
                                     processors=[ResizeToFill(150, 150)],
                                     format='JPEG',
                                     options={'quality': 100})
    banner_image=models.ImageField(upload_to='images/store/banner/', blank=True, null=True)
    banner_image_2530X460 = ImageSpecField(source='banner_image',
                                     processors=[ResizeToFill(2530, 460)],
                                     format='JPEG',
                                     options={'quality': 100})
    store_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(1190, 876)],
                                     format='JPEG',
                                     options={'quality': 100})
    storewise_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(150, 170)],
                                     format='JPEG',
                                     options={'quality': 100})
    location = models.ManyToManyField(Location, related_name='store_slocation', blank=True)
    eggless_price = models.FloatField(default=0.0)
    sugar_less_price = models.FloatField(default=0.0)
    flat_eggless = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        self.name = self.name.lower()
        super().save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return self.name
   
    @property
    def allProducts(self):
        return self.store_product.filter(is_available=True)[:12]

    @property
    def allLocations(self):
        return self.location.all()

    def get_absolute_url(self):
        return reverse('client:store-product-list', kwargs={'slug': self.slug})

    @property
    def vendorLink(self):
        from django.contrib.sites.models import Site
        current_site = Site.objects.get_current().domain+'/order/to/vendor/'+self.slug
        return current_site
        
    
    
    
    
    @property
    def avg_review(self):
        avg=StoreReview.get_average_rating_store(self.id)
        if avg:
            return float(avg)
        else:
            return 0

    @property
    def range(self):
        return range(0,int(self.avg_review)) 
    
    @property
    def get_average_product_review(self):
        from catalog.models import Product,ProductReview
        from django.db.models import Avg
        import math
        
        store_products = ProductReview.objects.filter(product__store=self)
        avg_product_review = ProductReview.objects.filter(product__store=self).aggregate(Avg('review_star')).get('review_star__avg',0)
        avg_product_review = avg_product_review if avg_product_review else 0
        return range(0,math.ceil(avg_product_review)) 
    
    @property
    def get_average_product_review_count(self):
        from catalog.models import Product,ProductReview
        from django.db.models import Avg
        import math
        
        
        avg_product_review = ProductReview.objects.filter(product__store=self).aggregate(Avg('review_star')).get('review_star__avg',0)
        avg_product_review = avg_product_review if avg_product_review else 0
        return avg_product_review
    
    @property
    def get_product_review_count(self):
        from catalog.models import Product,ProductReview
        from django.db.models import Avg
        import math
        
        store_products = ProductReview.objects.filter(product__store=self)
        count = ProductReview.objects.filter(product__store=self).count()
        return count
    
    

    


class StoreReview(models.Model):
    review_text = models.TextField()
    review_star = models.FloatField(default=0)
    store = models.ForeignKey(Store, related_name="store_review", on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='review_customer_store',
                                 on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    customer_purchased = models.BooleanField(default=False)

    def __int__(self):
        return self.review_star

    @classmethod
    def create_store_review(cls, review_text, review_star, store, customer, customer_purchased=False):
        from sales.models import OrderItem
        try:
            if OrderItem.objects.filter(order__customer=customer,product__product__store=store):
                customer_purchased=True
            return cls.objects.create(review_text=review_text, review_star=review_star, store=store, customer=customer,
                                      customer_purchased=customer_purchased)
        except:
            print("Review Creation Failed")

    @classmethod
    def update_store_review(cls, customer, store, review, review_star, review_text,customer_purchased=False):
        from sales.models import OrderItem
        try:
            # if (OrderItem.objects.filter(order__customer=customer, product__product__store=store).exists()):
            if OrderItem.objects.filter(order__customer=customer,product__product__store=store):
                customer_purchased=True
            # review = cls.objects.get(id=review.id)
            review.review_star = review_star
            review.review_text = review_text
            review.customer_purchased=customer_purchased
            review.save()
            return review
        except:
            print("Review Update Failed")

    @classmethod
    def get_star_value(cls, store):
        one_star = cls.objects.filter(store=store, review_star=1).count()
        two_star = cls.objects.filter(store=store, review_star=2).count()
        three_star = cls.objects.filter(store=store, review_star=3).count()
        four_star = cls.objects.filter(store=store, review_star=4).count()
        five_star = cls.objects.filter(store=store, review_star=5).count()

        return {
            'one_star': one_star*1,
            'two_star': two_star*2,
            'three_star': three_star*3,
            'four_star': four_star*4,
            'five_star': five_star*5,
        }
    
    @classmethod
    def get_star_count(cls, store):
        one_star = cls.objects.filter(store=store, review_star=1).count()
        two_star = cls.objects.filter(store=store, review_star=2).count()
        three_star = cls.objects.filter(store=store, review_star=3).count()
        four_star = cls.objects.filter(store=store, review_star=4).count()
        five_star = cls.objects.filter(store=store, review_star=5).count()

        return {
            'one_star': one_star,
            'two_star': two_star,
            'three_star': three_star,
            'four_star': four_star,
            'five_star': five_star,
        }
    
    @classmethod
    def percentage(cls,part, whole):
        try:
            return 100 * float(part)/float(whole)
        except:
            return 0
    
    @classmethod
    def get_star_percentage(cls, store):
        one_star = cls.objects.filter(store=store, review_star=1).count()
        two_star = cls.objects.filter(store=store, review_star=2).count()
        three_star = cls.objects.filter(store=store, review_star=3).count()
        four_star = cls.objects.filter(store=store, review_star=4).count()
        five_star = cls.objects.filter(store=store, review_star=5).count()
        total = float(one_star)+float(two_star)+float(three_star)+float(four_star)+float(five_star)

        return {
            'one_star': cls.percentage(one_star,total),
            'two_star': cls.percentage(two_star,total),
            'three_star': cls.percentage(three_star,total),
            'four_star': cls.percentage(four_star,total),
            'five_star': cls.percentage(five_star,total),
        }


    @classmethod
    def get_total_user_store_ratings(cls, store):
        return cls.objects.filter(store=store).count()

    @classmethod
    def get_average_rating_store(cls, store):
        from django.db.models import Avg
        try:
            counts = cls.get_star_value(store)
            total_counts = counts.get('one_star') + counts.get('two_star') + counts.get('three_star') + counts.get(
                'four_star') + counts.get('five_star')
            average_rating = total_counts / cls.get_total_user_store_ratings(store)
            return format(average_rating,'.1f')
        except:
            return 0
        

    @classmethod
    def get_ratings(cls,store):
        return cls.objects.filter(store=store)

    @property
    def range(self):
        return range(0,int(self.review_star)) 
    

class Factories(models.Model):
    name = models.CharField(max_length = 100)
    address = models.CharField(max_length = 100)
    # is_active=models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Factories'
        ordering = ('-id',)

    @property
    def get_user_id_of_the_factory(self):
        return self.factories.values('user__id')
