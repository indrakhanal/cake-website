from catalog.models import ProductAddons,SessionImage
from sales.models import *
from client.utils import eggSugarLessTotal,productAddontotal
from django.shortcuts import render, redirect, get_object_or_404
from settings.models import ShippingMethod
from rest_framework.response import Response
# from payment.models import CustomerDetail
from client.models import MenuItem1
from django.http import JsonResponse
from settings.models  import ShippingTime
import secrets




def placeOrderUnAuth(request,address):
    data=unAuthCalculation(request)
    
    order_number=secrets.token_hex(3)
    if Order.objects.filter(order_number=order_number).exists():
       order_number=order_number+secrets.token_hex(1)
    order = Order.objects.create(customer=None,
                   order_number=order_number,
                      discount=data.get('discount'),
                      coupon=data.get('coupon'),
                      sub_total_order = data.get('discounted_sub_total'),
                      shipping_cost=data.get('shipping_cost_total'),
                      delivery_address=address,
                      delivery_date=None,
                      total=data.get('discounted_total'),
                      tax_rate = None,
                      order_from = 'Direct',
                      order_status='Unconfirmed',
                      payment_status='Awaiting Payment',
                      )
    
  
    for item in data.get('cart_list'):
       varient=item.get('varient')
       addons=item.get('addons')
      #  addons_quantity=item.get('addons_quantity')
       is_eggless=item.get('eggless')
       is_sugarless=item.get('sugarless')
       
       if is_sugarless:
          is_sugarless=True
       else:
          is_sugarless=False
       
       if is_eggless:
          is_eggless=True
       else:
          is_eggless =False

      #  photo_image = SessionImage.get_session_image(item.get('key'))
       order_item=OrderItem.objects.create(order=order,
                               product=varient[0],
                               price=varient[0].selling_price,
                               quantity=item.get('quantity'),
                               sub_total=item.get('sub_total'),
                               total=item.get('total'),
                               special_instruction=item.get('message'),
                               is_sugerless=is_sugarless,
                               is_eggless=is_eggless,
                               date=item.get('date'),
                               time=item.get('time'),
                               shipping_method=item.get('shipping_method'),
                              #  photo_cake_image=photo_image,
                               pound=item.get('pound'),

                               )
       
       if addons and len(addons)>=1:
          a=0
          for i in addons:
             addon=get_object_or_404(ProductAddons,id=i["id"])
             AddonOrderItem.objects.create(order_item=order_item,addons=addon,quantity=i["addons_quantity"])
             a=a+1
       quantity=varient[0].quantity-item.get('quantity')
       ProductVarient.objects.filter(id=varient[0].id).update(quantity=quantity)
       if order:
          return True 
       else:
          return False
    
    # return {'order_number':order_number}   


def unAuthCalculation(request):
    cart_list = []
    cart_count = 0
    sub_total = 0
    addons_price_grand_total = 0
    sub_total_without_egg_sugar = 0
    shipping_cost_total = 0
    product_varient = request.data.get('product_varient')
    for varient in product_varient:
      # get_varient = ProductVarient.objects.get(id = int(varient['id']))
      quantity = int(varient['quantity'])
      varient_product = int(varient['id'])
      is_eggless = varient.get('is_eggless')
      is_sugarless = varient.get('is_sugarless')
      shipping_method = int(varient.get('shipping_method'))
      shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
      shipping_cost_total = shipping_cost_total + (shipping_method.price*quantity)
      pound = int(varient.get('pound'))
      message = varient.get('message')
      delivery_date = varient.get('date_delivery')
      time = varient.get('time')

      addons = varient.get('addons')
      # addons_quantity = varient.get('addons_quantity')
      coupon=varient.get('coupon',None)
      addons_price_total = productAddonTotal(addons)
      
      __varient = ProductVarient.objects.get(id=varient_product)
      varient = ProductVarient.objects.filter(id=varient_product)
      store = __varient.product.store

      varient_count = __varient.product.varientCount()
      cart_count = cart_count + int(quantity)

      egg_sugar_less_total_data = eggSugarLessTotal(store, is_eggless, is_sugarless,pound)
      egg_sugar_less_total = quantity * egg_sugar_less_total_data.get('egg_sugar_less_total')

      sub_total_without_egg_sugar = sub_total_without_egg_sugar + (__varient.selling_price * int(quantity))
      sub_total = sub_total_without_egg_sugar + egg_sugar_less_total

      
      
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
                        'eggless_price': egg_sugar_less_total_data.get('eggless_price'),
                        'sugarless_price': egg_sugar_less_total_data.get('sugarless_price'),
                        'display_price_with_egg_sugar_and_addon': display_price_with_egg_sugar_and_addon,
                        'date': delivery_date,
                        'time': time,
                        'delivery_time':get_object_or_404(ShippingTime,id=time),
                        'addon_total_price': addon_total_price,
                        'addons':addons,
                        # 'addons_quantity':addons_quantity,
                        'sub_total':sub_total_without_egg_sugar + egg_sugar_less_total,
                        'total':sub_total_without_egg_sugar + egg_sugar_less_total+shipping_method.price,
                        'shipping_method':shipping_method
                        
                        })
    total_without_shipping_cost = sub_total + addons_price_grand_total
    total_with_shipping_method = total_without_shipping_cost + shipping_cost_total
    discounted_total=total_with_shipping_method
    discounted_sub_total=total_without_shipping_cost
    
    discount=None
    if coupon:
      coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
      if coupon.coupon_type == 'Flat':
        discounted_sub_total=discounted_sub_total-coupon.value
        discount=coupon.value
        discounted_total = discounted_total - coupon.value
        
      if coupon.coupon_type == 'Percentage':
        discounted_sub_total=discounted_sub_total-coupon.value
        discount=(coupon.value/100)*total
        discounted_total = discounted_total - discount
        
    return {'cart_list': cart_list, 'total': sub_total,'cart_count': cart_count,'discount':discount,
            'total_with_shipping_method': total_with_shipping_method, 'shipping_cost_total': shipping_cost_total,'discounted_total':discounted_total,'discounted_sub_total':discounted_sub_total,'coupon':coupon,'total_without_shipping_cost':total_without_shipping_cost}



def unAuthtotalcouponCalculation(request):
    cart_list = []
    cart_count = 0
    sub_total = 0
    addons_price_grand_total = 0
    sub_total_without_egg_sugar = 0
    shipping_cost_total = 0
    product_varient = request.data.get('product_varient')
    for varient in product_varient:
      quantity = int(varient['quantity'])
      varient_product = int(varient['id'])
      is_eggless = varient.get('is_eggless')
      is_sugarless = varient.get('is_sugarless')
      pound = int(varient.get('pound'))
      
      addons = varient.get('addons')
      # addons_quantity = varient.get('addons_quantity')
      addons_price_total = productAddonTotal(addons)
      
      __varient = ProductVarient.objects.get(id=varient_product)
      store = __varient.product.store

      varient_count = __varient.product.varientCount()
      cart_count = cart_count + int(quantity)

      egg_sugar_less_total_data = eggSugarLessTotal(store, is_eggless, is_sugarless,pound)
      egg_sugar_less_total = quantity * egg_sugar_less_total_data.get('egg_sugar_less_total')

      sub_total_without_egg_sugar = sub_total_without_egg_sugar + (__varient.selling_price * int(quantity))
      sub_total = sub_total_without_egg_sugar + egg_sugar_less_total
      
      
      addons_price_grand_total = addons_price_grand_total + addons_price_total.get('addons_price_total')
      
      total_without_shipping_cost = sub_total + addons_price_grand_total
        
    return {'cart_count': cart_count,'total_without_shipping_cost':total_without_shipping_cost}


def productAddonTotal(addons):
    addons_price_total = 0
    addons_list = []
    i = 0
    if addons and len(addons) > 0:
        for item in addons:
            addons_price = ProductAddons.objects.only('price').get(id=item["id"])
            addons_price_total = float(addons_price_total) + (float(addons_price.price) * int(item["addons_quantity"]))
            addon_object = ProductAddons.objects.get(id=item["id"])
            addons_list.append({'addon_name': addon_object.name, 'addon_price': addon_object.price,
                                'addons_quantity': item["addons_quantity"]})
            i = i + 1
        return {'addons_price_total': addons_price_total, 'addons_list': addons_list}
    else:
        addons_price_total = 0
        return {'addons_price_total': addons_price_total, 'addons_list': addons_list}



