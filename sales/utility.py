from logging import exception
from catalog.models import *
from client.utils import eggSugarLessTotal
import secrets
from django.shortcuts import get_object_or_404
from settings.models import ShippingTime
from django.db.models import Q
from sales.models import Order,OrderItem,AddonOrderItem, OrderLogs
from client.utils import order_number_by_date
from datetime import datetime
import pytz
import requests
import json
from accounts.external_api import post_authenticate
from accounts.models import OdooTokenStore


def get_addons_price(addons):
   addons_price = 0
   for item in addons:
      addon = ProductAddons.objects.get(id=item)
      addons_price = addons_price + addon.price
   return addons_price

def get_addons_price_obj(addons):
   addons_price = 0
   for item in addons:
      addons_price = addons_price + item.price
   return addons_price


def get_order_number():
   order_number=secrets.token_hex(3)
   if Order.objects.filter(order_number=order_number).exists():
      order_number=order_number+secrets.token_hex(1)
   return order_number

def get_refrence_number():
   reference=secrets.token_hex(3)
   if Order.objects.filter(reference=reference).exists():
      reference=reference+secrets.token_hex(1)
   return reference

def get_time(time):
   return get_object_or_404(ShippingTime,id=time)

def get_shipping_cost(varient,delivery_type):
   total=0
   for i in varient:
      total=total+get_object_or_404(ShippingMethod,id=delivery_type).price*int(i.get('quantity'))
   return total
def get_addon_total(addons):
   total=0
   for i in addons:
      addon=ProductAddons.objects.get(id=i.get('addon'))
      quantity=i.get('quantity')
      total=total+addon.price*int(quantity)
   return total

import pdb
def get_sub_total(varient):
   total=0
   egg_sugar_less_total=0
   addon_total=0
   for i in varient:
      varient=get_object_or_404(ProductVarient,id=i.get('product'))
      total=total+float(varient.selling_price)*int(i.get('quantity'))
      store=varient.product.store
      if i.get('eggless') == 'on':
         is_eggless='yes'
      else:
         is_eggless=False
      if i.get('sugarless') == 'on':
         is_sugarless='yes'
      else:
         is_sugarless=False
      try:
         pound=varient.attribut_value.filter(Q(attribute__name='Weight') | Q(attribute__name='Quantity'))[0].value
      except:
         pound = 0
      egg_sugar_less_total=egg_sugar_less_total+eggSugarLessTotal(store, is_eggless, is_sugarless,float(pound)).get('egg_sugar_less_total')*int(i.get('quantity'))
      addon_total=addon_total+get_addon_total(i.get('addons'))
   total=total+egg_sugar_less_total+addon_total
   return total


def get_total(varient,delivery_type):
   return get_sub_total(varient)+get_shipping_cost(varient,delivery_type)

def item_get_sub_total(varient,eggless,sugarless,quantity,addons):
   total=float(varient.selling_price)*int(quantity)
   store=varient.product.store
   if eggless == 'on':
      is_eggless='yes'
   else:
      is_eggless=False
   if sugarless == 'on':
      is_sugarless='yes'
   else:
      is_sugarless=False
   pound=varient.attribut_value.filter(Q(attribute__name='Weight') | Q(attribute__name='Quantity'))[0].value
   egg_sugar_less_total=eggSugarLessTotal(store, is_eggless, is_sugarless,float(pound)).get('egg_sugar_less_total')*int(quantity)
   addon_total=get_addon_total(addons)
   return total+egg_sugar_less_total+addon_total

def item_get_shipping_cost(delivery_type,quantity):
   return get_object_or_404(ShippingMethod,id=delivery_type).price*int(quantity)

def item_get_total(varient,eggless,sugarless,quantity,addons,delivery_type):
   return item_get_sub_total(varient,eggless,sugarless,quantity,addons)+item_get_shipping_cost(delivery_type,quantity)

def createOrder(request,att,varient,message,delivery_type,delivery_date,delivery_time,payment_method,vendor,remarks):
   time=get_time(delivery_time)
   shipping_cost=get_shipping_cost(varient,delivery_type)
   total=get_total(varient,delivery_type)
   sub_total_order=get_sub_total(varient)
   
   order=Order.objects.create(order_number=order_number_by_date(),
      total=total,
      sub_total_order=sub_total_order,
      shipping_cost=shipping_cost,
      order_status='Unconfirmed',
      payment_status='Awaiting Payment',
      delivery_status='New',
      delivery_address=att,
      payment_method = payment_method,
      date=delivery_date,
      time=time,
      reference=get_refrence_number(),
      vendor =vendor,
      remarks=remarks,
      created_by=request.user,
      ) 
   for i in varient:
      varient=get_object_or_404(ProductVarient,id=i.get('product'))
      if i.get('eggless') == 'on':
         is_eggless=True
      else:
         is_eggless=False
      if i.get('sugarless') == 'on':
         is_sugarless=True
      else:
         is_sugarless=False

      flavour=None
      for j in varient.attribut_value.all():
         if j.attribute.name == 'Flavour':
            flavour=j.value
      item=OrderItem.objects.create(order=order,
                                 product=varient,
                                 name=varient.varient_name,
                                 flavour =flavour,
                                 price=varient.selling_price,
                                 quantity=i.get('quantity'),
                                 sub_total=item_get_sub_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons')),
                                 total=item_get_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons'),delivery_type),
                                 special_instruction=i.get('message'),
                                 is_sugerless=is_sugarless,
                                 is_eggless=is_eggless,
                                 shipping_method=get_object_or_404(ShippingMethod,id=delivery_type),
                                 photo_cake_image=i.get('image'),
                                 pound=varient.attribut_value.filter(Q(attribute__name='Weight') | Q(attribute__name='Quantity'))[0].value)
      addons=i.get('addons')
      for i in addons:
         addon=get_object_or_404(ProductAddons,id=i.get('addon'))
         AddonOrderItem.objects.create(order_item=item,addons=addon,quantity=i.get('quantity'),price = addon.price)
   return order


def updateOrder(request,att,varient,message,delivery_type,delivery_date,delivery_time,order,payment_method,vendor,remarks):
   time=get_time(delivery_time)
   shipping_cost=get_shipping_cost(varient,delivery_type)
   total=get_total(varient,delivery_type)
   sub_total_order=get_sub_total(varient)
   
   order_=Order.objects.filter(id=order.id).update(
      total=total,
      sub_total_order=sub_total_order,
      shipping_cost=shipping_cost,
      payment_method=payment_method,
      date=delivery_date,
      time=time,
      vendor=vendor,
      remarks=remarks,
      updated_by = request.user
      )
   undelete_item=[]
   for i in varient:
      varient=get_object_or_404(ProductVarient,id=i.get('product'))
      if i.get('eggless') == 'on':
         is_eggless=True
      else:
         is_eggless=False
      if i.get('sugarless') == 'on':
         is_sugarless=True
      else:
         is_sugarless=False

      if OrderItem.objects.filter(order__id=order.id,product__id=i.get('product')).exists():
         item = OrderItem.objects.filter(order__id=order.id,product__id=i.get('product'))
         if item[0].photo_cake_image:
            image = item[0].photo_cake_image
         else:
            image=i.get('image'),
         
         if item[0].photo_cake_image1:
            image1 = item[0].photo_cake_image1
         else:
            image1=i.get('image1'),

         if item[0].photo_cake_image2:
            image2 = item[0].photo_cake_image2
         else:
            image2=i.get('image2'),

         if item[0].photo_cake_image3:
            image3 = item[0].photo_cake_image3
         else:
            image3=i.get('image3'),

         flavour=None
         for j in varient.attribut_value.all():
            if j.attribute.name == 'Flavour':
                flavour=j.value
         item=OrderItem.objects.filter(order__id=order.id,product__id=i.get('product')).update(
                                 product=varient,
                                 name=varient.varient_name,
                                 flavour=flavour,
                                 price=varient.selling_price,
                                 quantity=i.get('quantity'),
                                 sub_total=item_get_sub_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons')),
                                 total=item_get_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons'),delivery_type),
                                 special_instruction=i.get('message'),
                                 is_sugerless=is_sugarless,
                                 is_eggless=is_eggless,
                                 shipping_method=get_object_or_404(ShippingMethod,id=delivery_type),
                                 pound=varient.attribut_value.filter(Q(attribute__name='Weight') | Q(attribute__name='Quantity'))[0].value,
                                 )
         item=OrderItem.objects.get(order__id=order.id,product__id=i.get('product'))  

         if i.get('image'):
            item.photo_cake_image=i.get('image')
            item.save()
         if i.get('image1'):
            item.photo_cake_image1=i.get('image1')
            item.save()
         if i.get('image2'):
            item.photo_cake_image2=i.get('image2')
            item.save()
         if i.get('image3'):
            item.photo_cake_image3=i.get('image3')
            item.save()
         undelete_item.append(item.id)
      else:
         item=OrderItem.objects.create(order=order,
                                 product=varient,
                                 price=varient.selling_price,
                                 quantity=i.get('quantity'),
                                 sub_total=item_get_sub_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons')),
                                 total=item_get_total(varient,i.get('eggless'),i.get('sugarless'),i.get('quantity'),i.get('addons'),delivery_type),
                                 special_instruction=i.get('message'),
                                 is_sugerless=is_sugarless,
                                 is_eggless=is_eggless,
                                 shipping_method=get_object_or_404(ShippingMethod,id=delivery_type),
                                 photo_cake_image=i.get('image'),
                                 photo_cake_image1=i.get('image1'),
                                 photo_cake_image2=i.get('image2'),
                                 photo_cake_image3=i.get('image3'),
                                 pound=varient.attribut_value.filter(Q(attribute__name='Weight') | Q(attribute__name='Quantity'))[0].value)
         undelete_item.append(item.id)
      addons=i.get('addons')
      undelete_addons=[]
      for i in addons:
         addon=get_object_or_404(ProductAddons,id=i.get('addon'))
         if AddonOrderItem.objects.filter(order_item__id=item.id,addons__id=addon.id).exists():
            AddonOrderItem.objects.filter(order_item__id=item.id,addons__id=addon.id).update(addons=addon,quantity=i.get('quantity'))
            undelete_addons.append(AddonOrderItem.objects.get(order_item__id=item.id,addons__id=addon.id).id)
         else:
            item_=AddonOrderItem.objects.create(order_item=item,addons=addon,quantity=i.get('quantity'),price = addon.price)
            undelete_addons.append(item_.id)
      deleteAddonsInItem(item,undelete_addons)
   deleteItemInOrder(order,undelete_item)
   return order

def deleteAddonsInItem(item,undelete_addons):
   for item in AddonOrderItem.objects.filter(order_item__id=item.id):
      if not item.id in undelete_addons:
         item.delete()

def deleteItemInOrder(order,undelete_item):
   for item in OrderItem.objects.filter(order_id=order.id):
      if not item.id in undelete_item:
         item.delete()



def createCustomOrder(request,att,custom_order_formset,delivery_type,delivery_date,delivery_time,shipping_cost,total,sub_total,payment_method,product,vendor,remarks):
   time=get_time(delivery_time)
   order=Order.objects.create(
      order_number=order_number_by_date(),
      total=total,
      sub_total_order=sub_total,
      shipping_cost=shipping_cost,
      order_status='Unconfirmed',
      payment_status='Awaiting Payment',
      delivery_status='New',
      delivery_address=att,
      payment_method=payment_method,
      date=delivery_date,
      time=time,
      reference=get_refrence_number(),
      vendor = vendor,
      remarks=remarks,
      created_by=request.user
      )
   for i,form in enumerate(custom_order_formset):
      if form.is_valid():
         data=form.cleaned_data

         item=OrderItem.objects.create(order=order,
                                    name=data.get('name')+'-'+str(data.get('weight'))+'-'+data.get('flavour'),
                                    flavour=data.get('flavour'),
                                    product_id=product[i].id,
                                    price=data.get('price'),
                                    quantity=1,
                                    sub_total=sub_total,
                                    total=total,
                                    special_instruction=data.get('message'),
                                    is_sugerless=data.get('is_sugarless'),
                                    is_eggless=data.get('is_eggless'),
                                    shipping_method=get_object_or_404(ShippingMethod,id=delivery_type),
                                    photo_cake_image=data.get('image'),
                                    photo_cake_image1=data.get('image1'),
                                    photo_cake_image2=data.get('image2'),
                                    photo_cake_image3=data.get('image3'),
                                    pound=data.get('weight'))
         addons=data.get('addons')
         for i in addons:
            addon=get_object_or_404(ProductAddons,id=i.id)
            AddonOrderItem.objects.create(order_item=item,addons=addon,quantity=1,price = addon.price)
   return order

from django.core import serializers
def createLog(request,order_instance):
   order_to_be_logged = serializers.serialize("json",Order.objects.filter(id=order_instance.id),fields=('order_number','total','sub_total_order','shipping_cost','coupon','discount','order_status','payment_status','delivery_status','payment_method','delivery_assigned','vendor__name'))
   order_item =serializers.serialize("json",OrderItem.objects.filter(order_id=order_instance.id),fields=('name','flavour','pound','price','quantity','sub_total','total','special_instruction','is_eggless','is_sugarless'))
   addons = serializers.serialize("json",AddonOrderItem.objects.filter(order_item__order_id=order_instance.id), fields=('quantity','price','addons__name'))
   OrderLogs.objects.create(order_id = order_instance.id,
      log_created_by = request.user,
      order_data_log = order_to_be_logged,
      order_item=order_item,
      addons=addons)
   
def get_trimmed_varient(varient_name):
   list_ = varient_name.split('-')
   print(list_, "---------")
   if list_[1] == "":
      del list_[1:3]
   if list_[2] == "":
      del list_[2:4]
   label = ""
   for i in range(len(list_)):
      if i == len(list_)-1:
            label+=f"{list_[i]}"
      else:
            label+=f"{list_[i]}-"
   return label


def sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, sales_username, sales_email):
   base_url = "http://ohocake.finliftconsulting.com.np"
   url = "/create/saleorder"
   update_url = "/update/saleorder"
   if OdooTokenStore.objects.first():
      obj_ = OdooTokenStore.objects.first()
      tokens = obj_.access_key
      session_id = obj_.session_key
   else:
      try:
         session_id, tokens, partner_id = post_authenticate()
      except Exception as e:
         status_ = "Failed"
         error = f"Error from odoo: {str(e)}"
         return status_, error
   # customer = "/api/res.partner"
   order_item_id = OrderItem.objects.filter(order__id=order_id).values("id")
   sales_line_id = []
   for i in order_item_id:
      sales_data = {}
      c_id = i.get("id")
      obj = get_object_or_404(OrderItem, id=c_id)
      dt = obj.order.created_on
      invoice_date = dt.strftime('%Y-%m-%d %H:%M:%S')
      accepted_on = obj.order.accepted_on
      if accepted_on:
         validity_date = accepted_on.strftime('%Y-%m-%d')
      else:
         validity_date = dt.strftime('%Y-%m-%d')
      name = obj.product.varient_name
      label = get_trimmed_varient(name)
      price = obj.price
      delivery_charge = obj.order.shipping_cost
      addons_item = obj.orderitem_addons.all()
      quantity = obj.quantity
      payment_source =  obj.order.payment_method
      payment_reference = obj.order.order_number
      ct_date = obj.order.date
      if ct_date:
         commitment_date = ct_date.strftime('%Y-%m-%d')
      else:
         commitment_date = dt.strftime('%Y-%m-%d')
      if addons_item:
         for j in addons_item:
            addons_data = {}
            addons_data["product_uom_qty"] = j.quantity
            addons_data["price_unit"] = j.price
            addons_data["name"] = j.addons.name
            sales_line_id.append(addons_data)

      if delivery_charge:
         delivery_data = {}
         delivery_data["product_uom_qty"] = 1
         delivery_data["price_unit"] = obj.order.shipping_cost
         delivery_data["name"] = "Delivery Charge"
         sales_line_id.append(delivery_data)
     
      sales_data["product_uom_qty"] = quantity
      sales_data["price_unit"] = price
      sales_data["name"] = label
      sales_line_id.append(sales_data)
   headers = {
            "access-token":tokens,
            "Content-type":"application/jsonp",
            "Cookie":session_id
      }
   
   vendor = obj.order.vendor
   if vendor:
      vendor_id = obj.order.vendor.id
      user_name = obj.order.vendor.name
      try:
         factory = obj.order.delivery_order.factory.name
      except:
         factory = None
      if factory == "Aloknagar":
         branch_id = "1"
      elif factory == "Basundhara":
         branch_id = "2"
      else:
         branch_id = None
      email = None
      phone = None
   else:
      user_name = obj.order.delivery_address.receiver_fullname
      email = obj.order.delivery_address.receiver_email
      phone = obj.order.delivery_address.receiver_contact_number1
      try:
         factory = obj.order.delivery_order.factory.name
      except:
         factory = None
      if factory == "Aloknagar":
         branch_id = "1"
      elif factory == "Basundhara":
         branch_id = "2"
      else:
         branch_id = None
      vendor_id = None

   data = {
      "partner_id":{
         "mobile":phone,
         "name":user_name,
         "email":email,
         # "vendor_id":33
      },
      # "payment_term_id": 3,
      "salesperson_id":{"name":sales_username,"email":sales_email},
      "rider_id":{
         "mobile":rider_phone,
         "name":rider_name,
         "email":rider_email
      },
      # "date_order": str(invoice_date),
      "validity_date": str(validity_date),
      "commitment_date":str(commitment_date),
      "payment_source" : payment_source,
      "order_reference":payment_reference,
      "client_order_ref": "Reference Sample",
      "sale_line_ids":sales_line_id,

      }
   if branch_id:
      data["branch_id"] = branch_id
   else:
      data["branch_id"] = "1"

   if vendor_id:
      data["partner_id"]["vendor_id"] = vendor_id
   
   datas_ = json.dumps(data, indent=4)
   print(datas_, "----------")
   invoice_id_ = Order.objects.filter(id=order_id).values('odoo_id')[0]
   try:
      if invoice_id_.get("odoo_id"):
         #logic for requesting for put or patch request
         p_data = {
            "rider_id":{"mobile":rider_phone,"name":rider_name,"email":rider_email},
            # "payment_term_id": 3,
            # "date_order": str(invoice_date),
            "validity_date": str(validity_date),
            "commitment_date":str(commitment_date),
            "payment_source" : payment_source,
            "order_reference":payment_reference,
            "client_order_ref": "Reference Sample",
            "sale_line_ids":sales_line_id,
            }
         if branch_id:
            p_data["branch_id"] = branch_id
         p_datas_ = json.dumps(p_data, indent=4)
         odoo_update_id  = invoice_id_.get("odoo_id")
         req = requests.patch('{0}{1}/{2}'.format(base_url,update_url,odoo_update_id ), headers=headers, data=p_datas_)

      else:
         #logic for requesting for post request
         req = requests.post('{0}{1}'.format(base_url,url), headers=headers, data=datas_)
      e = None
      # if the authentication failed from stored tokens
      print(req.status_code, "status")
      print(req.json(), "-----")

      if req.status_code == 401:
         session_id, tokens, partner_id = post_authenticate()
         headers = {
            "access-token":tokens,
            "Content-type":"application/jsonp",
            "Cookie":session_id
         }
         if invoice_id_.get("odoo_id"):
            #logic for requesting for put or patch request
            odoo_update_id  = invoice_id_.get("odoo_id")
            req = requests.patch('{0}{1}/{2}'.format(base_url,update_url,odoo_update_id ), headers=headers, data=p_datas_)
         else:
            #logic for requesting for post request
            req = requests.post('{0}{1}'.format(base_url,url), headers=headers, data=datas_)
      if req.status_code == 200:
         odoo_id = req.json()["data"][0]["id"]
         obj = Order.objects.filter(id = order_id).update(odoo_id=odoo_id)
         status = "Finished"
      else:
         status = "Failed"
         e = req.json()
      return status,e
   except Exception as e:
      return "Failed", str(e)

def get_salesperson(request):
   username = request.user.username
   email = request.user.email
   return username, email

# def updateOrderOdoo(order_id, rider_name):
#    invoice_id_ = Order.objects.filter(id=order_id).values('odoo_id')
#    import xmlrpc
#    if invoice_id_:
#       session_id, tokens, partner_id = post_authenticate()
#       url = "http://104.251.210.6:8017"
#       db = "ohocake_live"
#       username = "admin@finliftconsulting.com"
#       password = "admin@finliftconsulting.com"
#       endpoint_url = "/create/saleorder"
#       try:
#             obj = get_object_or_404(OrderItem, order__id=order_id)
#       except:
#          order_item_id = OrderItem.objects.filter(order__id=order_id).values("id")[0]
#          c_id = order_item_id.get("id")
#          obj = get_object_or_404(OrderItem, id=c_id)
#       invoice_date = obj.order.created_on
#       name = obj.product.varient_name
#       label = get_trimmed_varient(name)
#       price = obj.total
#       quantity = obj.quantity
#       payment_source =  obj.order.payment_method
#       payment_reference = obj.order.order_number
#       common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
#       uid = common.authenticate(db, username, password, {})
#       models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
#       ids = models.execute_kw(db, uid, password, 'account.move', 'search_read', [[['source_document', '=', payment_reference]]], {'fields': ['partner_id', 'id']})
     
#       invoice_id = invoice_id_[0].get("odoo_db_id")
#       partner_id_ = ids[0]['partner_id'][0]
#       headers = {
#                "access-token":tokens,
#                "Content-type":"application/jsonp",
#                "Cookie":session_id
#          }
#       api_invoice_line_id = [(1, invoice_id,{'name':label, 'price_unit':price, 'quantity':quantity})]
#       data = {
#          "partner_id":partner_id_,
#          "invoice_date":str(invoice_date),
#          "move_type":"out_invoice",
#          "__api__invoice_line_ids":str(api_invoice_line_id),
#          "payment_source":payment_source,
#          "source_document": payment_reference,
#          "rider":rider_name,
#       }
#       datas_ = json.dumps(data, indent=4)
#       req = requests.put(url+endpoint_url+str(invoice_id), headers=headers, data=datas_)
#       if req.status_code == 200:
#          status = "Success"
#       else:
#          status = "Failed"
#       return status
#    else:
#       sendOrderToOdoo(order_id, rider_name)
   