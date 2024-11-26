from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from .utils import get_unique_slug, compress
from mptt.models import MPTTModel, TreeForeignKey
import math
from django.core.files.storage import FileSystemStorage
import os
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from ckeditor_uploader.fields import RichTextUploadingField
from django.urls import reverse
from store.models import Store
from settings.models import ShippingMethod

class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=200, blank=True, null=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image = models.ImageField(upload_to='images/category/', blank=True, null=True, max_length=700)
    index_image_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(263, 263)],
                                     format='JPEG',
                                     options={'quality': 100})
    is_available = models.BooleanField(default=True)
    is_type = models.BooleanField(default=True)
    show_on_landing = models.BooleanField(default=True)
    display_order = models.IntegerField(default=1)


    class Meta:
        ordering = ('display_order', '-id',)
        verbose_name_plural = 'Category'



    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name

    def get_childrens(self):
      return self.get_children().order_by('display_order')

    @classmethod 
    def is_occasion(cls):
      occasions = ['occasion','occasions']

      for i in cls.objects.all():
        if i.name.lower() in occasions:
          return i
      return False

    def get_absolute_url(self):
        return reverse('client:category-product', kwargs={'slug': self.slug})





class Tags(models.Model):
    name = models.CharField(max_length=50)
    is_quick_filter=models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.name)

    class Meta:
        verbose_name_plural = 'Product Tags'
        ordering = ('-id',)


class Flavour(models.Model):
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150,unique=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return '{0}'.format(self.name)

    # def contain_product(self):
    #     if self.flavour.all().count() >= 1:
    #         return True

    

    def get_absolute_url(self):
        return reverse('client:flavour-product-lists', kwargs={'slug': self.slug})

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'name', 'slug')
        self.name = self.name.lower()
        super().save(force_insert, force_update, *args, **kwargs)


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name, max_length):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return super(OverwriteStorage, self).get_available_name(name, max_length)


class ProductAddons(models.Model):
    addon_types = (('Candle', 'Candle'),
                      ('Ballons', 'Ballons'),
                      ('Spray', 'Spray'),
                      ('Chocolates', 'Chocolates'),
                      ('Gifts', 'Gifts'),
                      ('Birthday Cards', 'Birthday Cards'),
                      ('Bouquet /Flowers','Bouquet /Flowers'),
                      ('Birthday Hats','Birthday Hats'),
                      ('Party Popper','Party Popper'),
                      ('Other','Other'),
                      )
    name = models.CharField(max_length=30, unique=True)
    types = models.CharField(max_length=20, choices=addon_types,default='Other')
    price = models.FloatField()
    addon_image = models.ImageField(upload_to='images/catalog/addons', blank=True, null=True, max_length=700)
    addon_image_350X350=ImageSpecField(source='addon_image',
                                     processors=[ResizeToFill(175, 175)],
                                     format='JPEG',
                                     options={'quality': 100})
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product Addons'
        ordering = ('-id',)

    



class Product(models.Model):
    name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=250, unique=True)
    store = models.ForeignKey(Store, related_name='store_product', null=True, on_delete=models.SET_NULL)
    description = models.TextField(max_length=250, blank=True, null=True)
    long_description = RichTextUploadingField('Long Description', blank=True, null=True)
    delivery_information = RichTextUploadingField('Delivery Information', blank=True, null=True)
    instruction = RichTextUploadingField('instruction', blank=True, null=True)
    image = models.ImageField(upload_to='images/catalog/products', blank=True, null=True, max_length=700)
    image_thumbnail_1204X920 = ImageSpecField(source='image',
                                     processors=[ResizeToFill(512, 460)],
                                     format='JPEG',
                                     options={'quality': 100})
    image_thumbnail_300X280=ImageSpecField(source='image',
                                     processors=[ResizeToFill(150, 140)],
                                     format='JPEG',
                                     options={'quality': 100})
    bestseller_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(283, 283)],
                                     format='JPEG',
                                     options={'quality': 100})
    listpage_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(255, 255)],
                                     format='JPEG',
                                     options={'quality': 100})

    shopwise_item_product = ImageSpecField(source='image',
                                     processors=[ResizeToFill(228, 228)],
                                     format='JPEG',
                                     options={'quality': 100})
    recomendation_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(267, 178)],
                                     format='JPEG',
                                     options={'quality': 100})
    cart_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(100, 120)],
                                     format='JPEG',
                                     options={'quality': 100})
    review_thumbnail = ImageSpecField(source='image',
                                     processors=[ResizeToFill(595, 438)],
                                     format='JPEG',
                                     options={'quality': 100})

    image1 = models.ImageField(upload_to='images/catalog/products', blank=True, null=True, max_length=700)
    image1_thumbnail_1204X920 = ImageSpecField(source='image1',
                                     processors=[ResizeToFill(512, 460)],
                                     format='JPEG',
                                     options={'quality': 100})
    image1_thumbnail_300X280=ImageSpecField(source='image1',
                                     processors=[ResizeToFill(150, 140)],
                                     format='JPEG',
                                     options={'quality': 100})
    image2 = models.ImageField(upload_to='images/catalog/products', blank=True, null=True, max_length=700)
    image2_thumbnail_1204X920 = ImageSpecField(source='image2',
                                     processors=[ResizeToFill(512, 460)],
                                     format='JPEG',
                                     options={'quality': 100})
    image2_thumbnail_300X280=ImageSpecField(source='image2',
                                     processors=[ResizeToFill(150, 140)],
                                     format='JPEG',
                                     options={'quality': 100})
    image3 = models.ImageField(upload_to='images/catalog/products', blank=True, null=True, max_length=700)

    image3_thumbnail_1204X920 = ImageSpecField(source='image3',
                                     processors=[ResizeToFill(512, 460)],
                                     format='JPEG',
                                     options={'quality': 100})
    image3_thumbnail_300X280=ImageSpecField(source='image3',
                                     processors=[ResizeToFill(150, 140)],
                                     format='JPEG',
                                     options={'quality': 100})
    category = models.ManyToManyField(Category, related_name='category')
    addons = models.ManyToManyField(ProductAddons, related_name='addons', blank=True)
    tags = models.ManyToManyField(Tags,blank=True,related_name='product_tags')
    related_products = models.ManyToManyField('self', blank=True, related_name='related_products')
    shipping_method = models.ManyToManyField(ShippingMethod,related_name='product_shipping_method',blank=True)
    flavour = models.ManyToManyField(Flavour, blank=True, related_name='flavour')
    is_available = models.BooleanField(default=True)
    is_best_seller = models.BooleanField(default=False)
    show_eggless = models.BooleanField(default=True)
    show_sugarless = models.BooleanField(default=True)
    is_recomended = models.BooleanField(default=False)
    min_order_time = models.FloatField(default=1)
    note = models.CharField(max_length = 200,blank=True,null=True)
    is_props = models.BooleanField(default=False)
    display_order = models.IntegerField(default=1)

    class Meta:
        ordering = ('display_order', '-id',)
        verbose_name_plural = 'Product'

    def __str__(self):
        return self.name
    
    def tags_card(self):
      for i in self.tags.all():
        if not i.is_quick_filter:
          return i

    def product_reviews_count(self):
      return self.product_review.all().count()
      

    def listing_product_varient(self):
        return self.product.order_by('display_order_varient').filter(status=True)[:1].get()

   
    @property
    def get_sugarless_price(self):
        if self.show_sugarless:
            return self.store.sugar_less_price
        else:
            return 0
    
    @property
    def is_cake_props(self):
        return self.is_props
    
    @property
    def get_eggless_price(self):
        if self.show_eggless:
            return self.store.eggless_price
        else:
            return 0
    
    @property
    def is_eggless_flat(self):
        if self.store.flat_eggless:
            return "yes"
        else:
            return "no"
        
    # def save(self, force_insert=False, force_update=False, *args, **kwargs):
    #     if not self.slug:
    #         self.slug = get_unique_slug(self, 'name', 'slug')
    #     self.name = self.name.lower()
    #     super().save(force_insert, force_update, *args, **kwargs)
    
    @property
    def get_min_order_date(self):
        import datetime
        from datetime import timedelta 
        
        min_order_time = self.min_order_time + 5.75
        min_date = (datetime.datetime.now() + timedelta(hours=min_order_time)).date()
        return min_date.strftime("%Y-%m-%d")


        
    @property
    def get_first_varient_attribute_name(self):
        try:
            product_varients = ProductVarient.objects.filter(product=self,status=True,quantity__gte=1).order_by('display_order_varient')
            for item  in product_varients:
              if item.attribut_value.filter(attribute__name='Weight').exists():
                return 'Weight'
              elif item.attribut_value.filter(attribute__name='Quantity').exists():
                return 'Quantity'
              else:
                return ""
        except:
            return ""
    @property
    def get_second_varient_attribute_name(self):
        try:
            product_varients = ProductVarient.objects.filter(product=self,status=True,quantity__gte=1).order_by('display_order_varient')
            for item  in product_varients:
              if item.attribut_value.filter(attribute__name='Flavour').exists():
                return 'Flavour'
              else:
                return ""
        except:
            return ""
       

    def first_varient_attributes(self):
        from ordered_set import OrderedSet
        try:
            first_attr_name=self.get_first_varient_attribute_name
            first_attr_value = AttributeValue.objects.filter(attribute_value__product=self,attribute_value__status=True,
                                                             attribute__name=first_attr_name,attribute_value__quantity__gte=1).order_by('attribute_value__display_order_varient')
            final = []
            for item in first_attr_value:
                final.append(item.value)
            return {'name': first_attr_name, 'value': list(OrderedSet(final))}
        except Exception as e:
            return []

    def second_varient_attributes(self):
        from ordered_set import OrderedSet
        
        try:
            second_attr_name=self.get_second_varient_attribute_name
            first_attr_value = AttributeValue.objects.filter(attribute_value__product=self,attribute_value__status=True,
                                                             attribute__name=second_attr_name,attribute_value__quantity__gte=1).order_by('attribute_value__display_order_varient')
            final = []
            for item in first_attr_value:
                final.append(item.value)
            return {'name': second_attr_name, 'value': list(OrderedSet(final))}
        except Exception as e:
            return []

    @property
    def get_related_products(self):
        if self.related_products.all():
            return self.related_products.filter(store__is_active=True).order_by('?')[:4]
        else:
            return Product.objects.filter(category__in = self.category.all(),store__is_active=True).order_by('?').exclude(id=self.id)[:4]
    
    @property
    def images(self):
        images_1204X920 = []
        images_300X280=[]
        if self.image:
            images_1204X920.append(self.image_thumbnail_1204X920.url)
            images_300X280.append(self.image_thumbnail_300X280.url)
        if self.image1:
            images_1204X920.append(self.image1_thumbnail_1204X920.url)
            images_300X280.append(self.image1_thumbnail_300X280.url)
        if self.image2:
            images_1204X920.append(self.image2_thumbnail_1204X920.url)
            images_300X280.append(self.image2_thumbnail_300X280.url)
        if self.image3:
            images_1204X920.append(self.image3_thumbnail_1204X920.url)
            images_300X280.append(self.image3_thumbnail_300X280.url)
        return {'images_1292X920':images_1204X920,'images_324X280':images_300X280}

    def get_absolute_url(self):
        return reverse('client:product-detail', kwargs={'slug': self.slug})

    def quantity(self):
        quantity = 0
        for i in self.product.filter(status=True):
            quantity = quantity + i.quantity
        return quantity


    def varientCount(self):
        return self.product.filter(is_available_varient=True,status=True).count()

    def varient_count_other(self):
        return self.product.filter(base_varient=False,status=True).count()

    
    def avg_review(self):
        
        avg=ProductReview.get_average_rating_product(self.id)
        if avg:
            return avg
        else:
            return 0

    def checkPhotoCakeStatus(self):
        photo_cakes=['Photo Cake','photocake','PhotoCake','PHOTO CAKE','photo cake','Photo Cakes','photocakes','PhotoCakes','PHOTO CAKES','photo cakes']
        for i in self.category.all():
            if i.name in photo_cakes:
                return True
        return False

    @classmethod
    def allowReview(cls,request,product): 
        if request.user.is_authenticated and OrderItem.objects.filter(order__customer=request.user,product__product=product,order__order_status='Complete').exists():
            return True
        return False
    
    @classmethod
    def is_reviewed(cls,request,product):
        if request.user.is_authenticated and ProductReview.objects.filter(customer=request.user,product=product).exists():
            return True
        return False

    @classmethod
    def quickFlavour(cls,product):
        return Flavour.objects.filter(flavour__in=product).distinct()
    
    @classmethod
    def quickOccasion(cls,product):
      category=Category.objects.filter(category__in=product,is_available=True).distinct()
      category_=[]
      for i in category:
        if str(i.get_root()).lower() in ['occasion','occasions']:
          category_.append(i)
      return category_
    
    @classmethod
    def quickTagsFilter(cls,product):
      tags=Tags.objects.filter(product_tags__in=product,is_quick_filter=True).distinct()
      return tags
    
    @classmethod
    def quickCategory(cls,product):
      from django.db.models import Q
      category=Category.objects.filter(Q(parent=None) & ~Q(name__in=['Occasion','OCCASION','occasion','occasions','OCCASIONS','Occasions']) & Q(is_available=True)).distinct().order_by('display_order')[:3]
      return category

    @property
    def addonListTypes(self):
        addons = self.addons.all()
        types = []
        for item in addons:
            if not item.types in types:
                types.append(item.types)
        types_list=[]
        for i in types:
            types_list.append({
                'type':i,
                'addons':ProductAddons.objects.filter(types=i,addons=self)
                })
        return types_list


    @property
    def in_stock(self):
        count = ProductVarient.objects.filter(product=self,status=True,quantity__gte=1)
        if count:
            return True
        else:
            return False

class Attribute(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, related_name='attribute', on_delete=models.CASCADE)
    value = models.CharField(max_length=250)

    def __str__(self):
        return "{0}-{1}".format(self.attribute, self.value)


class ProductVarient(models.Model):
    varient_name = models.CharField(max_length=200, )
    slug = models.SlugField(max_length=200, unique=True)
    product = models.ForeignKey(Product, related_name='product', on_delete=models.CASCADE)
    old_price = models.FloatField()
    price = models.FloatField(blank=True, null=True)
    cost_price = models.FloatField(blank=True, null=True)
    product_code = models.CharField(max_length=250, blank=True, null=True)
    quantity = models.IntegerField()
    attribut_value = models.ManyToManyField(AttributeValue, related_name='attribute_value', blank=True)
    is_available_varient = models.BooleanField(default=True)
    display_order_varient = models.IntegerField(default=1)
    base_varient = models.BooleanField(default=False)
    status=models.BooleanField(default=True)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if not self.slug:
            self.slug = get_unique_slug(self, 'varient_name', 'slug')
        self.varient_name = self.varient_name.lower()
        super().save(force_insert, force_update, *args, **kwargs)

    def __str__(self):
        return self.varient_name
  

    def in_stock(self):
        if self.is_available_varient and self.quantity >= 1:
            return True

    @classmethod
    def remove_varient_edit(cls, request_list_1, list_2):
      from django.db.models import ProtectedError
      delete_id_row = list(set(list_2) - set(request_list_1))
      for i in delete_id_row:
        try:
          ProductVarient.objects.filter(id=i).delete()
        except ProtectedError:
          ProductVarient.objects.filter(id=i).update(status=False)
          

    @property
    def selling_price(self):
        if self.price:
            return self.price
        else:
            return self.old_price

    def discount(self):
        if self.price:
            discount = (((self.old_price - self.price) / self.old_price) * 100)
            return math.ceil(discount)

    
    @property
    def attribute_val1(self):
      if self.attribut_value.filter(attribute__name='Weight').exists():
        print('i am  at val one')
        return self.attribut_value.filter(attribute__name='Weight')[0].value
      elif self.attribut_value.filter(attribute__name='Quantity').exists():
        print('i am val two')
        return self.attribut_value.filter(attribute__name='Quantity')[0].value
      else:
        print('i am at val 3')
        return None
    
    @property
    def attribute_val2(self):
      if self.attribut_value.filter(attribute__name='Flavour').exists():
        return self.attribut_value.filter(attribute__name='Flavour')[0].value
      else:
        return None

    @property
    def attribute_name1(self):
      if self.attribut_value.filter(attribute__name='Weight').exists():
        return 'Weight'
      elif self.attribut_value.filter(attribute__name='Quantity').exists():
        return 'Quantity'
      else:
        return None
        
    @property
    def attribute_name2(self):
      if self.attribut_value.filter(attribute__name='Flavour').exists():
        return 'Flavour'

      
    
from sales.models import Order,OrderItem
class ProductReview(models.Model):
    review_text = models.TextField()
    review_star = models.FloatField(default=0)
    product = models.ForeignKey(Product, related_name="product_review", on_delete=models.CASCADE)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='review_customer',
                                 on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True)
    customer_purchased = models.BooleanField(default=False)

    def __str__(self):
        return self.product.name

    @classmethod
    def create_product_review(cls, review_text, review_star, product, customer, customer_purchased=False):
        try:
            if OrderItem.objects.filter(order__customer=customer,product__product=product):
                customer_purchased=True
            return cls.objects.create(review_text=review_text, review_star=review_star, product=product,
                                      customer=customer, customer_purchased=customer_purchased)
        except:
            print("Review Creation Failed")

    @classmethod
    def update_product_review(cls, customer, product, review, review_star, review_text,customer_purchased=False):
        from sales.models import OrderItem
        try:
            if OrderItem.objects.filter(order__customer=customer,product__product=product):
                customer_purchased=True
            review.review_star = review_star
            review.review_text = review_text
            review.customer_purchased=customer_purchased
            review.save()

        except:
            print("Review Update Failed")

    @classmethod
    def get_star_value(cls, product):
        one_star = cls.objects.filter(product=product, review_star=1).count()
        two_star = cls.objects.filter(product=product, review_star=2).count()
        three_star = cls.objects.filter(product=product, review_star=3).count()
        four_star = cls.objects.filter(product=product, review_star=4).count()
        five_star = cls.objects.filter(product=product, review_star=5).count()

        return {
            'one_star': one_star*1,
            'two_star': two_star*2,
            'three_star': three_star*3,
            'four_star': four_star*4,
            'five_star': five_star*5,
        }
    
    @classmethod
    def get_star_count(cls, product):
        one_star = cls.objects.filter(product=product, review_star=1).count()
        two_star = cls.objects.filter(product=product, review_star=2).count()
        three_star = cls.objects.filter(product=product, review_star=3).count()
        four_star = cls.objects.filter(product=product, review_star=4).count()
        five_star = cls.objects.filter(product=product, review_star=5).count()

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
    def get_star_percentage(cls, product):
        one_star = cls.objects.filter(product=product, review_star=1).count()
        two_star = cls.objects.filter(product=product, review_star=2).count()
        three_star = cls.objects.filter(product=product, review_star=3).count()
        four_star = cls.objects.filter(product=product, review_star=4).count()
        five_star = cls.objects.filter(product=product, review_star=5).count()
        total = float(one_star)+float(two_star)+float(three_star)+float(four_star)+float(five_star)

        return {
            'one_star': cls.percentage(one_star,total),
            'two_star': cls.percentage(two_star,total),
            'three_star': cls.percentage(three_star,total),
            'four_star': cls.percentage(four_star,total),
            'five_star': cls.percentage(five_star,total),
        }
    
    

    
   
    @classmethod
    def get_total_user_product_ratings(cls, product):
        return cls.objects.filter(product=product).count()

    @classmethod
    def get_average_rating_product(cls, product):
        from django.db.models import Avg
        try:
            counts = cls.get_star_value(product)
            total_counts = counts.get('one_star') + counts.get('two_star') + counts.get('three_star') + counts.get(
                'four_star') + counts.get('five_star')
            average_rating = total_counts / cls.get_total_user_product_ratings(product)
            
            return format(average_rating,'.1f')
        except:
            return 0
        

    @classmethod
    def get_ratings(cls,product):
        return cls.objects.filter(product=product,)

    @property
    def range(self):
        return range(0,int(self.review_star)) 

    @classmethod
    def reviewed_or_not(cls,request,product):
        if cls.objects.filter(product=product,customer=request.user).exists():
            return cls.objects.get(product=product,customer=request.user)
        return None



class SessionImage(models.Model):
    unique_id = models.CharField(blank=True,null=True,max_length = 700)
    image = models.ImageField(upload_to='images/session-images/', blank=True, null=True, max_length=700)

    def __int__(self):
        return self.review_star
    
    @classmethod
    def store_session_image(cls,unique_id,image):
        try:
            if image:
                cls.objects.create(unique_id=unique_id,image=image)
        except Exception as e:
            print("Session Image exception:", e)
    
    @classmethod
    def get_session_image(cls,key):
        try:
            if cls.objects.filter(unique_id=key).exists():
                return cls.objects.get(unique_id=key).image
            else:
                return None
        except Exception as e:
            print("Session Image exception:", e)
