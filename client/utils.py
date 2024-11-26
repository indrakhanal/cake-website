from catalog.models import ProductAddons,SessionImage
from sales.models import *
from django.shortcuts import render, redirect, get_object_or_404
from settings.models import ShippingMethod
# from payment.models import CustomerDetail
from client.models import MenuItem1
from django.http import JsonResponse
from settings.models  import ShippingTime



# def unique_order_item_number():
#   import secrets
#   order_item_number=secrets.token_hex(3)
#   if OrderItem.objects.filter(order_item_number=order_item_number).exists():
#     order_item_number=order_item_number+secrets.token_hex(1)
#   return order_item_number

def productAddontotal(addons, addons_quantity):
    addons_price_total = 0
    addons_list = []
    i = 0
    if addons and len(addons) > 0:
        for item in addons:
            addons_price = ProductAddons.objects.only('price').get(id=item)
            addons_price_total = float(addons_price_total) + (float(addons_price.price) * int(addons_quantity[i]))
            addon_object = ProductAddons.objects.get(id=item)
            addons_list.append({'addon_name': addon_object.name, 'addon_price': addon_object.price,
                                'addons_quantity': addons_quantity[i]})
            i = i + 1
        return {'addons_price_total': addons_price_total, 'addons_list': addons_list}
    else:
        addons_price_total = 0
        return {'addons_price_total': addons_price_total, 'addons_list': addons_list}

def eggSugarLessTotal(store, is_eggless, is_sugarless,pound):

    if store.flat_eggless:
        if is_eggless == 'yes' and is_sugarless == 'yes':
            egg_sugar_less_total = store.sugar_less_price + store.eggless_price
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price,
                    'sugarless_price': store.sugar_less_price}
        if is_eggless == 'yes' and not is_sugarless:
            egg_sugar_less_total = store.eggless_price
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price,
                    'sugarless_price': 0}
        if is_sugarless == 'yes' and not is_eggless:
            egg_sugar_less_total = store.sugar_less_price
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': 0,
                    'sugarless_price': store.sugar_less_price}
        else:
            return {'egg_sugar_less_total': 0, 'eggless_price': 0, 'sugarless_price': 0}
    else:
        if is_eggless == 'yes' and is_sugarless == 'yes':
            egg_sugar_less_total = store.sugar_less_price + (store.eggless_price * pound)
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price * pound,
                    'sugarless_price': store.sugar_less_price}
        if is_eggless == 'yes' and not is_sugarless:
            egg_sugar_less_total = store.eggless_price * pound
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': store.eggless_price * pound,
                    'sugarless_price': 0}
        if is_sugarless == 'yes' and not is_eggless:
            egg_sugar_less_total = store.sugar_less_price
            return {'egg_sugar_less_total': egg_sugar_less_total, 'eggless_price': 0,
                    'sugarless_price': store.sugar_less_price}
        else:
            return {'egg_sugar_less_total': 0, 'eggless_price': 0, 'sugarless_price': 0}

def sessionCalculation(request):
    cart_list = []
    cart_count = 0
    sub_total = 0
    addons_price_grand_total = 0
    sub_total_without_egg_sugar = 0
    shipping_cost_total = 0
    is_unique_item_only=0
    for key, item in request.session.items():
      try:
        # if not key in single_variable_session():
        # if key:
          varient_product = item[0].get('product_varient')
          quantity = int(item[0].get('quantity'))
          is_eggless = item[0].get('is_eggless')
          is_sugarless = item[0].get('is_sugarless')
          shipping_method = item[0].get('shipping_method')
          shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
          shipping_cost_total = shipping_cost_total + (shipping_method.price*quantity)
          pound = int(item[0].get('pound'))
          message = item[0].get('message')
          delivery_date = item[0].get('date_delivery')
          time = item[0].get('time')
          unique_key = item[0].get('key')

          __varient = ProductVarient.objects.get(id=varient_product)
          varient = ProductVarient.objects.filter(id=varient_product)
          store = __varient.product.store

          varient_count = __varient.product.varientCount()
          cart_count = cart_count + int(quantity)

          egg_sugar_less_total_data = eggSugarLessTotal(store, is_eggless, is_sugarless,pound)
          egg_sugar_less_total = quantity * egg_sugar_less_total_data.get('egg_sugar_less_total')

          sub_total_without_egg_sugar = sub_total_without_egg_sugar + (__varient.selling_price * int(quantity))
          sub_total = sub_total_without_egg_sugar + egg_sugar_less_total

          addons = item[0].get('addons')
          addons_quantity = item[0].get('addons_quantity')
          addons_price_total = productAddontotal(addons, addons_quantity)
          addons_price_grand_total = addons_price_grand_total + addons_price_total.get('addons_price_total')
          addon_total_price = addons_price_total.get('addons_price_total')

          base_product = __varient.product.name
          description = __varient.product.description
          image = __varient.product.image
          display_price = __varient.selling_price * int(quantity)
          display_price_with_egg_sugar_and_addon = __varient.selling_price * int(
              quantity) + egg_sugar_less_total + addons_price_total.get('addons_price_total')

          cart_list.append({'varient': varient, 'display_price': display_price,
                            'base_product': base_product, 'quantity': quantity, 'varient_count': varient_count,
                            'message': message, 'pound': pound, 'eggless': is_eggless, 'sugarless': is_sugarless,
                            'eggless_price': egg_sugar_less_total_data.get('eggless_price')*int(quantity),
                            'sugarless_price': egg_sugar_less_total_data.get('sugarless_price')*int(quantity),
                            'display_price_with_egg_sugar_and_addon': display_price_with_egg_sugar_and_addon,
                            'date': delivery_date,
                            'time': time,
                            'delivery_time':get_object_or_404(ShippingTime,id=time),
                            'addon_total_price': addon_total_price,
                            'addons':addons,
                            'addons_quantity':addons_quantity,
                            'sub_total':sub_total_without_egg_sugar + egg_sugar_less_total,
                            'total':sub_total_without_egg_sugar + egg_sugar_less_total+shipping_method.price,
                            'shipping_method':shipping_method,
                            'key':unique_key
                            
                            })
          is_unique_item_only=is_unique_item_only+1
      except:
        continue
        # request.session.flush()
    total_without_shipping_cost = sub_total + addons_price_grand_total
    total_with_shipping_method = total_without_shipping_cost + shipping_cost_total
    discounted_total=total_with_shipping_method
    discounted_sub_total=total_without_shipping_cost
    coupon=None
    discount=None
    if 'coupon' in request.session:
      coupon =request.session['coupon']
      coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
      if coupon.coupon_type == 'Flat':
        discounted_sub_total=discounted_sub_total-coupon.value
        discount=coupon.value
        discounted_total = discounted_total - coupon.value
        
      if coupon.coupon_type == 'Percentage':
        discount=(coupon.value/100)*discounted_sub_total
        discounted_sub_total = discounted_sub_total-discount
        discounted_total = discounted_total - discount
        
    return {'cart_list': cart_list, 'sub_total': sub_total,'cart_count': cart_count,'discount':discount,
            'total_with_shipping_method': total_with_shipping_method, 'shipping_cost_total': shipping_cost_total,'discounted_total':discounted_total,'discounted_sub_total':discounted_sub_total,'coupon':coupon,'total_without_shipping_cost':total_without_shipping_cost,'is_unique_item_only':is_unique_item_only}

def updateCouponInCartOrSession(request):
    if not request.user.is_authenticated:
        if 'coupon' in request.session:
            del request.session['coupon']
    if request.user.is_authenticated:
        Cart.objects.filter(user=request.user).update(coupon=None)


# def validate_order_request(receiver_fullname,receiver_address,receiver_number1,receiver_number2,sender_full_name,sender_phone_number,receiver_email,sender_email,payment_method):
def validate_order_request(receiver_fullname,receiver_address,receiver_number1,sender_full_name,sender_phone_number,receiver_email,sender_email,payment_method,sender_address,city,area):
    from django.core.validators import validate_email
    from store.models import Location as StoreLocation
    
    if not receiver_fullname:
        return  'Enter receiver full name.'

    if  city:
      try:
        get_object_or_404(StoreLocation,id=city)
      except:
        return  'Select valid city.'
    else:
      return  'Select city.'

    if area:
      try:
        get_object_or_404(StoreLocation,id=area)
      except:
        return  'Select valid area.'
    else:
      return  'Select area.'

    if not receiver_address:
        return 'Enter receiver address.'

    if not receiver_number1 or not receiver_number1.isdigit() or len(receiver_number1) < 10:
        return 'Receiver contact number must be digit equal to 10.'

    if not sender_full_name:
        return 'Enter sender full name.'

    if not sender_phone_number or not sender_phone_number.isdigit() or len(receiver_number1) < 10:
      return 'Sender contact number must be digit equal to 10'
    
    if not sender_address:
      return 'Enter sender address.'

    if receiver_email:
        try:
            validate_email(receiver_email)
        except:
            return 'Receiver email is invalid.'

    if sender_email:
        try:
            validate_email(sender_email)
        except:
            return 'Sender email is invalid.'
    else:
        return 'Enter sender email.'

    if not payment_method:
        return 'Please select valid payment method.'

    return None


def single_variable_session():
    return ["_auth_user_id","_auth_user_backend","_auth_user_hash","_password_reset_key","coupon","location_id","account_verified_email","account_user"]
              
def validate_cart_quantity(request,settings_object):
    if not request.user.is_authenticated:
         user_obj=None
         data=sessionCalculation(request)
         total=data.get('discounted_total')
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


"""Return possible distinct(unique) order in cart"""
def getDistinctItems(request):
  distinct_order_keys_list=[]
  for key, item in request.session.items():
    try:
      if not item[0].get('distinct_order_keys') in distinct_order_keys_list:
        distinct_order_keys_list.append(item[0].get('distinct_order_keys'))
    except:
      continue
  return distinct_order_keys_list


"""For placing unique order and calculationg dublicate cartitem before placing order"""
class DistinctOrderCalculation():
  def __init__(self,request,item):
    self.request=request
    self.item=item
    
  def discountedTotal(self):
    return self.discountedSubTotal()+self.shippingCostTotal()
  
  def discount(self):
    if 'coupon' in self.request.session:
      coupon =self.request.session['coupon']
      coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
      if coupon.coupon_type == 'Flat':
        discount=coupon.value
        return discount
      if coupon.coupon_type == 'Percentage':
        discount=(coupon.value/100)* self.discountedSubTotal()
        return discount
    return 0
        
  def discountedSubTotal(self):
    sub_total=0
    for i in self.request.session.items():
      try:
        if str(i[1][0].get('distinct_order_keys'))==str(self.item):
          varient_product = i[1][0].get('product_varient')
          quantity = int(i[1][0].get('quantity'))
          is_eggless = i[1][0].get('is_eggless')
          is_sugarless = i[1][0].get('is_sugarless')
          pound = int(i[1][0].get('pound'))
          __varient = ProductVarient.objects.get(id=varient_product)
          store = __varient.product.store
          egg_sugar_less_total_data = eggSugarLessTotal(store, is_eggless, is_sugarless,pound)
          egg_sugar_less_total = quantity * egg_sugar_less_total_data.get('egg_sugar_less_total')
          sub_total = sub_total + egg_sugar_less_total+(__varient.selling_price * int(quantity))
          addons = i[1][0].get('addons')
          addons_quantity = i[1][0].get('addons_quantity')
          addons_price_total = productAddontotal(addons, addons_quantity)
          sub_total=sub_total+addons_price_total.get('addons_price_total')
      except:
        continue
    sub_total=sub_total-self.discount()
    return sub_total

  """Return total shipping cost of same order that may contain multiple item in cart"""
  def shippingCostTotal(self):
    shipping_cost_total=0
    for i in self.request.session.items():
      try:
        if str(i[1][0].get('distinct_order_keys'))==str(self.item):
          shipping_method = i[1][0].get('shipping_method')
          quantity=i[1][0].get('quantity')
          shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
          shipping_cost_total = shipping_cost_total + (shipping_method.price*int(quantity))
      except:
        continue
    return shipping_cost_total

  def commonOrderItem(self):
    commonOrderItems=[]
    for i in self.request.session.items():
      try:
        if str(i[1][0].get('distinct_order_keys'))==str(self.item):
          commonOrderItems.append(i[1][0])
      except:
        continue
    return commonOrderItems
  
  """Return subtotal of single item in cart"""
  def singleItemSubTotal(self,key):
    sub_total=0
    if str(key) in self.request.session:
      item=self.request.session[str(key)][0]
      varient_product = item.get('product_varient')
      quantity = int(item.get('quantity'))
      is_eggless = item.get('is_eggless')
      is_sugarless = item.get('is_sugarless')
      pound = int(item.get('pound'))
      __varient = ProductVarient.objects.get(id=varient_product)
      store = __varient.product.store
      egg_sugar_less_total_data = eggSugarLessTotal(store, is_eggless, is_sugarless,pound)
      egg_sugar_less_total = int(quantity) * egg_sugar_less_total_data.get('egg_sugar_less_total')
      sub_total =sub_total + egg_sugar_less_total + int( __varient.selling_price * int(quantity))
      addons = item.get('addons')
      addons_quantity = item.get('addons_quantity')
      addons_price_total = productAddontotal(addons, addons_quantity)
      sub_total=sub_total+addons_price_total.get('addons_price_total')
      return sub_total
  
  """Return unique date of dublicate item (unique order date)"""
  def Date(self):
    for i in self.request.session.items():
      try:
        if str(i[1][0].get('distinct_order_keys'))==str(self.item):
          date=i[1][0].get('date_delivery')
          return date 
      except:
        continue

  """Return unique time of dublicate cart item (unique order time)"""
  def Time(self):
    for i in self.request.session.items():
      try:
        if str(i[1][0].get('distinct_order_keys'))==str(self.item):
          time=i[1][0].get('time')
          time=get_object_or_404(ShippingTime,id=time)
          return time 
      except:
        continue
import pdb
"""Placing order when user is not authenticated"""
def placeOrderUnauth(request,user_obj,address):
    distinct_items=getDistinctItems(request)
    reference=secrets.token_hex(3)
    if Order.objects.filter(reference=reference).exists():
      reference=reference+secrets.token_hex(1)
    for item in distinct_items:
      data=DistinctOrderCalculation(request,item)
      shipping_cost=data.shippingCostTotal()
      discounted_subtotal=data.discountedSubTotal()
      discounted_total=data.discountedTotal()
      discount=data.discount()
      if 'coupon' in request.session:
        coupon = request.session['coupon']
      else:
        coupon=None
    
      date=data.Date()
      time=data.Time()
    
      
      # order_number=secrets.token_hex(3)
      # if Order.objects.filter(order_number=order_number).exists():
      #    order_number=order_number+secrets.token_hex(1)
      order_number = order_number_by_date()
      
      order = Order.objects.create(customer=user_obj,
                     order_number=order_number,
                        discount=discount,
                        coupon=coupon,
                        sub_total_order = discounted_subtotal,
                        shipping_cost=shipping_cost,
                        delivery_address=address,
                        date=date,
                        time=time,
                        total=discounted_total,
                        order_status='Unconfirmed',
                        payment_status='Awaiting Payment',
                        delivery_status='New',
                        reference=reference,
                        )
      for item in data.commonOrderItem():
         time=get_object_or_404(ShippingTime,id=item.get('time'))
         date=item.get('date_delivery')
         varient=item.get('product_varient')
         varient=get_object_or_404(ProductVarient,id=varient)
         addons=item.get('addons')
         addons_quantity=item.get('addons_quantity')
         is_eggless=item.get('is_eggless')
         is_sugarless=item.get('is_sugarless')
         quantity=item.get('quantity')
         shipping_method=ShippingMethod.objects.get(id=item.get('shipping_method'))
         item_keys_in_session=str(varient.product.id)+str(varient.id)+str(date)+str(time.id)
         sub_total=data.singleItemSubTotal(item_keys_in_session)
         total=sub_total+(int(quantity)*shipping_method.price)
         if is_sugarless=='yes':
            is_sugarless=True
         else:
            is_sugarless=False
         if is_eggless=='yes':
            is_eggless=True
         else:
            is_eggless =False
         flavour=None
         for i in varient.attribut_value.all():
            if i.attribute.name == 'Flavour':
                flavour=i.value
         photo_image = SessionImage.get_session_image(item.get('key'))
         order_item=OrderItem.objects.create(order=order,
                                 name=varient.varient_name,
                                 flavour=flavour,
                                 product=varient,
                                 price=varient.selling_price,
                                 quantity=quantity,
                                 sub_total=sub_total,
                                 total=total,
                                 special_instruction=item.get('message'),
                                 is_sugerless=is_sugarless,
                                 is_eggless=is_eggless,
                                 shipping_method=shipping_method,
                                 photo_cake_image=photo_image,
                                 pound=item.get('pound'),
                                 )
         if addons and len(addons)>=1:
            a=0
            for i in addons:
               addon=get_object_or_404(ProductAddons,id=i)
               AddonOrderItem.objects.create(order_item=order_item,addons=addon,quantity=addons_quantity[a],price=addon.price)
               a=a+1
         # quantity=varient.quantity-int(item.get('quantity'))
         # ProductVarient.objects.filter(id=varient.id).update(quantity=quantity)
    request.session.flush()
    return {'reference':reference}   

"""Return same varient total quantity in session cart by adding 1 to it"""
def calculateSameVarientTotalInSession(request,varient_):
  total_quantity=0
  for key,items in request.session.items():
    # if not key in single_variable_session():
    try:
      if items[0].get('product_varient') == varient_.id:
        total_quantity=total_quantity+int(items[0].get('quantity'))
    except:
      continue
  return total_quantity+1



"""Add product to session cart when user is not authenticated"""
def addToSession(request,key,quantity,varient_,product,addons,addons_quantity,date_delivery,time,message,pound,is_eggless,is_sugarless,shipping_method,unique_id,menu,distinct_order_keys):
  same_varient_total=calculateSameVarientTotalInSession(request,varient_)
  
  if same_varient_total <= varient_.quantity:
    if str(key) in request.session:
        old_quantity = str(request.session[str(key)][0]['quantity'])
        new_quantity = int(quantity) + int(old_quantity)
        if new_quantity > varient_.quantity:
            return 'error' 
        del request.session[str(key)]
        menu1 = []
        menu1.append(
            MenuItem1(distinct_order_keys,product, varient_.id, new_quantity, addons, addons_quantity, date_delivery, time,
                      message, pound, is_eggless, is_sugarless, shipping_method,unique_id).serialize())
        request.session[str(key)] = menu1
        return 'success'
    else:
        request.session[str(key)] = menu
        return 'success'
  return 'error'



def update_new_location(location_slug,request):
    from store.models import Location as StoreLocation
    if location_slug:
        location = get_object_or_404(StoreLocation, slug=location_slug)
        StoreLocation.store_location_id_in_session(request,location.id)

import pdb
import datetime
def order_number_by_date():
    order = Order.objects.first()
    if order.placed_on == datetime.date.today():
        order_number =order.order_number
        order_number = order_number.split('-')[-1]
        order_number = int(order_number)+1
        return str(datetime.date.today()) +'-'+ str(order_number)
    return str(datetime.date.today()) + '-'+str(1)






