from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,permissions,mixins
from sales.models import *
from .serializers import *
from sales.api.utils import placeOrderUnAuth,unAuthCalculation
from catalog.models import *
# from payment.models import CustomerDetail
from marketing.models import CartCoupon
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse,HttpResponse
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import generics
from rest_framework import serializers
import secrets
from client.utils import validate_order_request,validate_cart_quantity
from settings.models import *
from rest_framework.generics import ListAPIView

from django.forms.models import model_to_dict
import django_filters
from django.db.models import Q

from django.contrib.auth.models import User

from datetime import date, datetime, timezone, timedelta
from rest_framework.decorators import api_view
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

@api_view(('GET',))
@parser_classes([JSONParser])
def calculation_of_coupon(request,coupon):
      if request.user.is_authenticated:
        print('user',request.user)
      
        try:
              Cart.objects.get(user=request.user)
        except:
              Cart.objects.create(user=request.user)
        cart = get_object_or_404(Cart, user=request.user)
        cart_coupon = get_object_or_404(CartCoupon,coupon_number=coupon)
        print('cart_coupon',cart_coupon)
        if cart_coupon:
         cart_lists = cart.cart_list_jsonResponse
         cart_count = cart.cart_count()
         discounted_total = cart.discounted_total()
         discounted_sub_total = cart.discounted_sub_total()
         sub_total = cart.get_sub_total()
         total_without_shipping_cost = cart.get_sub_total()
         total_with_shipping_method = cart.get_total_with_shipping_method()
         shipping_cost_total = cart.get_shipping_price_total()
         get_list={'total_with_shipping_method':total_with_shipping_method,'cart_lists':cart_lists,
                  'cart_count':cart_count,'discounted_total':discounted_total,'discounted_sub_total':
                  discounted_sub_total,'sub_total':sub_total,'total_without_shipping_cost':total_without_shipping_cost,
                  'shipping_cost_total':shipping_cost_total}         
         return Response(get_list)
      else:
         return Response({'message':'failed'},status=status.HTTP_400_BAD_REQUEST)

@api_view(('GET','POST'))
@parser_classes([JSONParser])
def applycoupon(request):
  coupon_number = (request.data.get('coupon', None))
  response=totalFromApplyCoupon(request)
  if response.get('error')== True:
    return JsonResponse({'error': 'No item in your cart.', 'coupon': coupon_number})
  total=response.get('total')
  cart_count=response.get('cart_count')
  try:
      coupon = CartCoupon.objects.get(coupon_number=coupon_number, is_active=True)
      current_time = datetime.now(timezone.utc).date()
      coupon_per_user_limit = coupon.per_user_limit
      coupon_limit = coupon.total_user_limit
      min_cart_amount = coupon.min_cart_price
      max_cart_amount = coupon.max_cart_price
      time_limit = coupon.time_limit
      coupon_total_used = Order.objects.filter(~Q(order_status='Cancelled'), coupon=coupon).count()

      check_time_validity = current_time < time_limit
      check_price_range_validity = min_cart_amount <= total <= max_cart_amount
      check_total_coupon_limit_validity = coupon_total_used < coupon_limit
      if check_time_validity and check_price_range_validity and check_total_coupon_limit_validity:
          response=CartCoupon.getTotalAfterCouponApply(request,coupon.coupon_number,total)
          total=response.get('total')
          previous_total=response.get('previous_total')
          return JsonResponse({'status': 'Success', 'coupon': model_to_dict(coupon),'total':total,'previous_total':previous_total})
      else:
          return JsonResponse(
              {'error': 'Cart requirement unfulfilled.', 'coupon': coupon_number, 'min_value': min_cart_amount,
               'max_value': max_cart_amount, 'validity_date': coupon.time_limit})
  except:
      return JsonResponse({'error': 'Invalid Coupon.', 'coupon': coupon_number})



def totalFromApplyCoupon(request):
  if not request.user.is_authenticated:
     from sales.api.utils import unAuthtotalcouponCalculation
     data = unAuthtotalcouponCalculation(request)
     total=data.get('total_without_shipping_cost')
     return {'total':total,'cart_count':data.get('cart_count')}
        
  if request.user.is_authenticated:
     from sales.models import Cart
     cart = get_object_or_404(Cart, user=request.user)
     cart_count = cart.cart_count()
     if cart.cart_count() >= 1:
         total = cart.get_sub_total()
         return {'total':total,'cart_count':cart.cart_count()}
     else:
         return {'error':True}


@api_view(('GET','POST'))
@parser_classes([JSONParser])
def checkoutcart(request):
      product_varient = request.data.get('product_varient', None)
      quantity = request.data.get('quantity', 1)
      if not quantity:
          quantity = 1
      addons = request.data.get('addons')
      date_delivery = request.data.get('date_delivery', None)
      time = str(request.data.get('time',None))
      if not time:
          return JsonResponse({'error':'Please select time.'})
      message = request.data.get('message', None)
      # redirect_to_checkout = request.data.get('redirect_to_checkout', '')
      is_eggless = request.data.get('is_eggless', None)
      is_sugarless = request.data.get('is_sugarless', None)
      pound = request.data.get('pound', None)
      shipping_method = (request.data.get('shipping_method'))
      photo_for_photo_cake = request.FILES.get('photo_for_photo_cake',"")
      #product_ = get_object_or_404(Product, id=product)
      #print('product',product_)
      varient_ = get_object_or_404(ProductVarient, id=product_varient)
      if not varient_.quantity < 1 and not varient_.quantity < int(quantity) and int(quantity) >= 1:
          if request.user.is_authenticated:
              # pdb.set_trace()
              cart = Cart.objects.get(user=request.user)
              shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
              varient = get_object_or_404(ProductVarient, id=product_varient)
              print('varient',varient)
              CartItem.apiaddToCart(cart, varient_, date_delivery, time, is_eggless, is_sugarless, message,
                                 shipping_method, pound, quantity, addons,photo_for_photo_cake)
              return JsonResponse({'status': 'Success','cart_count':cart.cart_count()})
              
      else:
          return JsonResponse({'error': 'Selected quantity is not available on stock'})

  
class ListRetrieveCartView(mixins.ListModelMixin,
                           # mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   serializer_class = CartSerializer
   permission_classes = (permissions.IsAuthenticated,)
   def get_queryset(self):
      user =self.request.user
      return Cart.objects.filter(user=user).order_by('-id')


class CreateUpdateDestroyCartView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   serializer_class = CartSerializer
   permission_classes = (permissions.IsAuthenticated,)
   # def get_queryset(self):
   #    user =self.request.user
   #    return Cart.objects.filter(user=user).order_by('-id')

   def create(self, request):
        print("--------------------")
        user=self.request.user
        coupon=request.data.get('coupon')        
        if Cart.objects.filter(user=user,coupon=coupon):
            cart=Cart.objects.get(user=user,coupon=coupon)
            update = update_cart(user,coupon,cart)
            if update:
               return Response({'message':'success:cart updated successfully'}, status=status.HTTP_201_CREATED)
            else:
               return Response({'message':'fail:cart update fail'}, status=401)
        else:
            create = create_cart(user,coupon)
            if create:
               return Response({'message':'success:Cart create successfully'}, status=status.HTTP_201_CREATED)
            else:
               return Response({'message':'fail: Cart create failed'}, status=401)
        return Response({'message':'fail:permission or review update denied'}) 

def update_cart(user,coupon,cart):
   try:
            cart.user = user
            cart.coupon = coupon
            cart.save()
            return cart
   except:
      print("Cart Update Failed")
def create_cart(user,coupon):
   try:
            return Cart.objects.create(user=user,coupon=coupon)
   except:
      print("Cart Creation Failed")


class CartItemFilter(django_filters.FilterSet):
    class Meta:
        model = CartItem
        fields = ['is_eggless','is_sugarless']

class ListRetrieveCartItemView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   serializer_class = CartItemReadSerializer
   permission_classes = (permissions.IsAuthenticated,)
   filter_class = CartItemFilter
   def get_queryset(self):
      user=self.request.user
      cartitem=get_object_or_404(Cart,user=user)
      items=CartItem.objects.filter(cart=cartitem)
      return items

class CreateUpdateDestroyCartItemView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   serializer_class = CartItemWriteSerializer
   permission_classes = (permissions.IsAuthenticated,)
   def get_queryset(self):
      user=self.request.user
      cartitem=get_object_or_404(Cart,user=user)
      items=CartItem.objects.filter(cart=cartitem)
      return items
   
   def create(self, request):
        user = self.request.user
        product = request.data.get('product')
        quantity = request.data.get('quantity')
        date = request.POST.get('date')
        time = request.POST.get('time')
        message = request.data.get('message')
        shipping_method = request.POST.get('shipping_method')
        is_eggless = request.POST.get('is_eggless')
        is_sugarless = request.POST.get('is_sugarless')
        pound = request.POST.get('pound')
        photo_cake_image = request.POST.get('photo_cake_image')
        cart_user = Cart.objects.get(user = user)

        try:
           CartItem.objects.create(quantity=int(quantity),cart=cart_user,product_id=int(product),date=date,
            time=time,message=message,shipping_method_id=int(shipping_method),is_eggless=bool(is_eggless),
            is_sugarless=bool(is_sugarless),pound=pound,photo_cake_image=photo_cake_image)
           return Response({'message':'success'}, status=status.HTTP_201_CREATED) 
        except Exception as e:
           return Response({'message':str(e)}, status=401)  

class OrderFilter(django_filters.FilterSet):
    class Meta:
        model = Order
        fields = ['order_number','delivery_sent_nepxpress']

class ListRetrieveOrderView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   serializer_class = OrderReadSerializer
   permission_classes = (permissions.IsAuthenticated,)
   filter_class = OrderFilter
   def get_queryset(self):
      user =self.request.user
      return Order.objects.filter(customer=user).order_by('-id')

class CreateUpdateDestroyOrderView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Order.objects.order_by('-id').all()
   serializer_class = OrderWriteSerializer
   # permission_classes = (permissions.IsAuthenticated,)
   def get_queryset(self):
      user =self.request.user
      return Order.objects.filter(customer=user).order_by('-id')
   
   def create(self, request):
        # user = self.request.user
        if request.user.is_authenticated:
         user = request.user
        else:
         user = None 
        # customer=get_object_or_404(User,username=user)
      #   order_number = request.data.get('order_number')
      #   total = request.data.get('total')
      #   sub_total_order = request.data.get('sub_total_order')
      #   shipping_cost = request.data.get('shipping_cost')
      #   coupon = request.data.get('coupon')
      #   discount = request.data.get('discount')
      #   refunded_amount = request.data.get('refunded_amount')
      #   order_status = request.data.get('order_status')
      #   payment_status = request.data.get('payment_status')
        get_delivery_address = request.data.get('delivery_address')
      #   customer_notes = request.data.get('customer_notes')
      #   created_on = request.data.get('created_on')
      #   order_from = request.data.get('order_from')
      #   tax_rate = request.data.get('tax_rate')
      #   cart_item = request.data.get('cart_item')
      #   cart_items=[]
      #   for item in cart_item:
      #      cart_items.append(CartItem.objects.get(id=int(item)))
      #   print('items',cart_items)

        receiver_fullname=get_delivery_address['receiver_fullname']
        receiver_email = get_delivery_address['receiver_email']
        receiver_address = get_delivery_address['receiver_delivery_address']
        landmark = get_delivery_address.get('landmark',None)
        address_type = get_delivery_address.get('receiver_address_type')
        receiver_number1 = get_delivery_address.get('receiver_contact_number1')
        receiver_number2 = get_delivery_address.get('receiver_contact_number2',None)

        occasion = get_delivery_address['occasion']
        sender_full_name = get_delivery_address['sender_fullname']
        sender_email = get_delivery_address['sender_email']
        sender_address = get_delivery_address.get('sender_address',None)
        sender_phone_number = get_delivery_address['contact_number']
        payment_method = get_delivery_address.get('payment_method',None)
        hide_info_from_receiver = get_delivery_address['hide_info_from_receiver']
      #   i_am_receiver = get_delivery_address['i_am_receiver']
        response = validate_order_request(receiver_fullname,receiver_address,receiver_number1,sender_full_name,sender_phone_number,receiver_email,sender_email,payment_method,sender_address)
        if response:
           return Response({'message':response},status=401)

        settings_object = Settings.objects.all().get()
        response=api_validate_cart_quantity(request,settings_object)
        if response:
            return Response({'message':response},status=401)

        delivery_address=create_delivery_address(user,receiver_fullname,
            receiver_email,receiver_address,landmark,address_type,receiver_number1,
            receiver_number2,occasion,sender_full_name,sender_phone_number,sender_email,
            hide_info_from_receiver)
      #   delivery_address=get_object_or_404(DeliveryAddress,id=delivery_address_id)

        if delivery_address:

           if not request.user.is_authenticated:
                response=placeOrderUnAuth(request,delivery_address)
                if response:
                  return Response({'message':'success'}, status=status.HTTP_201_CREATED)
                else:
                  return Response({'message':'Order place failed'})

           if self.request.user.is_authenticated:
                     cart=get_object_or_404(Cart,user=self.request.user)
                     sub_total_sales = cart.get_sub_total()
                     total=cart.discounted_total()
                     sub_total = cart.discounted_sub_total()
                     order_number=secrets.token_hex(3)
                     if Order.objects.filter(order_number=order_number).exists():
                        order_number=order_number+secrets.token_hex(1)
                     discount=cart.discount
                     coupon=cart.coupon
                     shipping_cost=cart.get_shipping_price_total()
                     order=Order.placeOrderAuth(user,order_number,discount,coupon,sub_total,shipping_cost,delivery_address,total,cart)
                     # CustomerDetail.create_customer_detail(order.order_number)
                     CartItem.objects.filter(cart=cart).delete()
                     return Response({'message':'success'}, status=status.HTTP_201_CREATED)

           else:
               return Response({'message':"You arenot authenticated"})
        else:
            return Response({'message':"failed"}) 
         

      #   try:
      #      delivery_address_id=create_delivery_address(user,get_delivery_address).id
      #      get_delivery_address=get_object_or_404(DeliveryAddress,id=delivery_address_id)
      #      instance = order_create(customer,order_number,total,sub_total_order,shipping_cost,coupon,
      #      discount,order_status,payment_status,tax_rate,get_delivery_address,created_on,order_from,cart_items)
      #      print(instance,'instance')
           

         #   for item in get_items:
         #      get_item=get_object_or_404(OrderItem,id=item)
         #      instance.items.add(get_item)
      #      return Response({'message':'success'}, status=status.HTTP_201_CREATED) 
      #   except Exception as e:
      #      return Response({'message':str(e)}, status=401)  
      

def create_delivery_address(user,receiver_fullname,
            receiver_email,receiver_address,landmark,address_type,receiver_number1,
            receiver_number2,occasion,sender_full_name,sender_phone_number,sender_email,
            hide_info_from_receiver):
   delivery_address_created = DeliveryAddress.objects.create(receiver_fullname=receiver_fullname,
   receiver_email=receiver_email,receiver_delivery_address=receiver_address,
   receiver_address_type=address_type,receiver_contact_number1=receiver_number1,
   receiver_contact_number2=receiver_number2,occasion=occasion,sender_fullname=sender_full_name,
   sender_email=sender_email,contact_number=sender_phone_number,
   hide_info_from_receiver=hide_info_from_receiver,customer=user)
   print('delivery_address_create',delivery_address_created.id)
   return delivery_address_created


def api_validate_cart_quantity(request,settings_object):
  if not request.user.is_authenticated:
         user_obj=None
         data=unAuthCalculation(request)
         total=data.get('total')
         cart_count=data.get('cart_count')
      
  if request.user.is_authenticated:
        user_obj = request.user
        cart=get_object_or_404(Cart,user=request.user)
        cart_count=cart.cart_count()
        total=cart.get_sub_total()
   
         
  if float(total) < float(settings_object.minimum_order_price):
        return 'Minimum cart requirement is a subtotal of '+ str(settings_object.minimum_order_price)
        
  if cart_count<=0:
        return 'You do not have item in cart.' 

class OrderView(viewsets.ModelViewSet):
   queryset = Order.objects.order_by('-id').all()
   serializer_class = OrderSerializer
   permission_classes = (permissions.IsAuthenticated,)


class IsStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class DeliveryNepView(viewsets.ModelViewSet):
   queryset = DeliveryNepxpress.objects.order_by('-id').all()
   serializer_class = DeliveryNepSerializer
   permission_classes = (IsStaffUser,)
   
   def list(self, request, *args, **kwargs):
        raise MethodNotAllowed("GET")

   def create(self, request, *args, **kwargs):
      data = request.data
      check_status = Order.objects.filter(order_number = data['order_number']).exists()

      if check_status:
         try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            data = {"message":"Post Successful"}
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
         except:
            data = {"message":"Delivery Post Exception."}
            return Response(data,status= status.HTTP_500_INTERNAL_SERVER_ERROR)
      else:
         data = {"message":"Order number doesn't exists"}
         return Response(data,status=status.HTTP_400_BAD_REQUEST)


from sales.models import OrderDelivery
from sales.api.serializers import OrderDeliverySerializer
from datetime import date as d
class DeliveryOrderAssignedToDeliveryBoy(APIView):
  def get(self, request, *args, **kwargs):
    today=d.today()
    queryset=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing'])
    serializer=OrderDeliverySerializer(queryset,many=True)
    return Response(serializer.data)


class OrderITemDeliveryStatusChange(APIView):
   def post(self, request, *args, **kwargs):
      order=get_object_or_404(Order,order_number=request.data['order_number'])
      if order.delivery_order.user == request.data['user']:
         Order.objects.filter(order_number=request.data['order_number']).update(delivery_status=request.data['delivery_status'])
         return Response(status=status.HTTP_200_OK)
      else:
         return Response(status=status.HTTP_400_BAD_REQUEST)


class SendingDetailToVendor(APIView):
  def get(self, request, *args, **kwargs):
    today=d.today()
    queryset=Order.objects.filter(date=today,order_status__in=['Confirmed','Processing'])
    serializer=VendorOrderSerializer(queryset,many=True)
    return Response(serializer.data)
        # items__product__product__store__slug=self.kwargs['slug'],





