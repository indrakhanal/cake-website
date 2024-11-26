from django.db import models
from django.shortcuts import get_object_or_404
from store.models import Store
from catalog.models import Category,Product

class CartCoupon(models.Model):
   option=(("Flat",'Flat Price'),
      ("Percentage",'Percentage')
      )
   coupon_type=models.CharField(max_length=250,choices=option)
   value=models.FloatField()
   coupon_number=models.CharField(max_length=50,unique=True)
   total_user_limit=models.IntegerField()
   per_user_limit=models.IntegerField()
   time_limit=models.DateField()
   min_cart_price=models.FloatField()
   max_cart_price=models.FloatField()
   store=models.ForeignKey(Store,related_name='coupon_store',blank=True,null=True,on_delete=models.CASCADE)
   category=models.ManyToManyField(Category,related_name='coupon_category',blank=True)
   product=models.ManyToManyField(Product,related_name='coupon_product',blank=True)
   is_active=models.BooleanField(default=True)
   
   def __str__(self):
      return self.coupon_number

   @classmethod
   def totalToApplyCoupon(cls,request):
      if not request.user.is_authenticated:
         from client.utils import sessionCalculation
         if request.session.values():
          data = sessionCalculation(request)
          if data.get('is_unique_item_only') == 1:
            total=data.get('total_without_shipping_cost')
            return {'total':total,'cart_count':data.get('cart_count')}
          else:
            return {'error':True}
         else:
             return {'error':True}
        
      if request.user.is_authenticated:
         from sales.models import Cart
         cart = get_object_or_404(Cart, user=request.user)
         cart_count = cart.cart_count()
         if cart.cart_count() >= 1 and cart.is_unique_item_only == 1:
             total = cart.get_sub_total()
             return {'total':total,'cart_count':cart.cart_count()}
         else:
             return {'error':True}



   @classmethod
   def getTotalAfterCouponApply(cls,request,coupon_number,total):
      if not request.user.is_authenticated:
         from client.utils import sessionCalculation
         request.session['coupon'] = coupon_number
         if 'coupon' in request.session:
            coupon = request.session['coupon']
            coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
            previous_total = total
            if coupon.coupon_type == 'Flat':
                total = total - coupon.value
            if coupon.coupon_type == 'Percentage':
                total = total - (coupon.value / 100 * total)
      
      if request.user.is_authenticated:
         from sales.models import Cart
         Cart.objects.filter(user=request.user).update(coupon=coupon_number)
         cart = get_object_or_404(Cart, user=request.user)
         if cart.coupon:
            coupon = get_object_or_404(CartCoupon, coupon_number=cart.coupon)
            previous_total = total
            if coupon.coupon_type == 'Flat':
               total = total - coupon.value
            if coupon.coupon_type == 'Percentage':
               total = total - (coupon.value / 100 * total)
      return {'total':total,'previous_total':previous_total}