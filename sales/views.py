import json
from django.views.generic import TemplateView
from django.http import Http404
from django.contrib import messages, auth
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import *
from settings.models import OutletBranch
from django.db.models import ProtectedError
from datetime import datetime
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from .forms import *
from catalog.models import *
from settings.models import *
from django.http import JsonResponse
from utility.send_email import send_email_to_user
from utility.hostname import hostname_from_request
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from allauth.account.signals import user_logged_in, user_signed_up
from django.dispatch.dispatcher import receiver
# from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from accounts.views import custom_permission_required as permission_required,SuperUserCheck
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Count

from store.models import Location
from store.models import Factories
from store.forms import FactoryModelForm
from sales.utility import sendOrderToOdoo



@receiver(user_logged_in, dispatch_uid="unique")
def user_logged_in_(request, user, **kwargs):
    """Adding session cart data into cart after login"""
    if request.user.is_authenticated:
        if Cart.objects.filter(user=request.user):
            try:
                Cart.objects.filter(user=request.user).update(coupon=None)
                cart = Cart.objects.get(user=request.user)
            except Cart.DoesNotExist:
                raise Http404
        else:
            cart = Cart.objects.create(user=request.user)
              
        if request.session.values():
            for key,item in request.session.items():
                try:
                    product_varient=item[0].get("product_varient")
                    product_varient=ProductVarient.objects.get(id=product_varient)
                    quantity=item[0].get('quantity')
                    date_delivery=item[0].get('date_delivery')
                    time=item[0].get('time')
                    message=item[0].get('message')
                    pound=item[0].get('pound')
                    shipping_method=item[0].get('shipping_method')
                    shipping_method=ShippingMethod.objects.get(id=shipping_method)
                    is_eggless=item[0].get('is_eggless')
                    is_sugarless=item[0].get('is_sugarless')
                    addons=item[0].get('addons')
                    addons_quantity=item[0].get('addons_quantity')
                    key = item[0].get('key')
                    image = SessionImage.get_session_image(key)
                    CartItem.addToCart(cart,product_varient,date_delivery,time,is_eggless,is_sugarless,message,shipping_method,pound,quantity,addons,addons_quantity,image)
                except:
                    continue
            if 'coupon' in request.session:
                coupon=request.session['coupon']
                cart.coupon=coupon
                cart.save()

        

"""Return Order list"""
class OrderList(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name = "admin_view/orders/order.html"
    permission_required = ['sales.view_order']
    
    def get(self,request,*args,**kwargs):
        from datetime import datetime
        # overall_filter_type= self.request.GET.get('overall_filter_type','hundred')
        # if overall_filter_type == 'hundred':
        #     qs = Order.objects.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status').order_by('-id')[:100]
        # else:
        qs = Order.objects.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status').order_by('-id')
        order_keyword = self.request.GET.get('order_keyword',None)
        order_by_type = self.request.GET.get('order_by_type',1)
        date_req = self.request.GET.get('date_range',None)
        date__range=self.request.GET.get('date_range',None)
        order_status = self.request.GET.getlist('order_status')
        payment_status = self.request.GET.getlist('payment_status')
        branch_names = OutletBranch.objects.filter(is_active=True).all()

        if date__range and len(date__range)<1:
            return redirect(self.request.META['HTTP_REFERER'])

        if order_status and payment_status:
            qs=Order.objects.filter(Q(order_status__in=order_status) & Q(payment_status__in=payment_status)).values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
        
        if order_status and not payment_status:
            qs=Order.objects.filter(order_status__in=order_status).values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
        
        if not order_status and payment_status:
            qs=Order.objects.filter(payment_status__in=payment_status).values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')

        if order_keyword:
            qs=Order.objects.filter(Q(customer__email__icontains=order_keyword) | Q(order_number__icontains=order_keyword) | Q(reference__icontains=order_keyword)).values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
        if date__range:
            date__range=date__range.split('to')
            if len(date__range)>1:
                start = date__range[0].strip()
                end=date__range[1].strip()
                start_date = datetime.strptime(start, '%Y-%m-%d').date()
                end_date = datetime.strptime(end, '%Y-%m-%d').date()
                if int(order_by_type) == 1:
                    qs=Order.objects.filter(placed_on__range=[start_date,end_date])
                    if payment_status and order_status:
                        qs = qs.filter(Q(order_status__in=order_status) & Q(payment_status__in=payment_status))
                    if payment_status and not order_status:
                        qs = qs.filter(payment_status__in=payment_status)
                    if not payment_status and order_status:
                        qs = qs.filter(order_status__in=order_status)
                    qs = qs.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
                if int(order_by_type) == 2:
                    qs=Order.objects.filter(date__range=[start_date,end_date])
                    if payment_status and order_status:
                        qs = qs.filter(Q(order_status__in=order_status) & Q(payment_status__in=payment_status))
                    if payment_status and not order_status:
                        qs = qs.filter(payment_status__in=payment_status)
                    if not payment_status and order_status:
                        qs = qs.filter(order_status__in=order_status)
                    qs = qs.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
            else:
                start = date__range[0]
                start_date = datetime.strptime(start, '%Y-%m-%d').date()
                if int(order_by_type) == int(1):
                    qs=Order.objects.filter(placed_on=start_date)
                    if payment_status and order_status:
                        qs = qs.filter(Q(order_status__in=order_status) & Q(payment_status__in=payment_status))
                    if payment_status and not order_status:
                        qs = qs.filter(payment_status__in=payment_status)
                    if not payment_status and order_status:
                        qs = qs.filter(order_status__in=order_status)
                    qs = qs.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
                if int(order_by_type) == int(2):
                    qs=Order.objects.filter(date=start_date)
                    if payment_status and order_status:
                        qs = qs.filter(Q(order_status__in=order_status) & Q(payment_status__in=payment_status))
                    if payment_status and not order_status:
                        qs = qs.filter(payment_status__in=payment_status)
                    if not payment_status and order_status:
                        qs = qs.filter(order_status__in=order_status)
                    qs = qs.values('id','order_number','reference','delivery_address__contact_number','created_on','total','payment_method','order_status','payment_status')
        paginator = Paginator(qs, 50)
        try:
           page_number = request.GET.get('page')
           if page_number is None:
               page_number=1

           qs = paginator.get_page(page_number)
        except PageNotAnInteger:
           qs = paginator.get_page(1)
        except EmptyPage:
           qs = paginator.get_page(paginator.num_pages)

        return super(OrderList,self).get(request,order_list=qs, order_status=order_status,payment_status=payment_status,date_range_req = date_req,order_keyword=order_keyword,branches=branch_names,order_by_type=int(order_by_type), page_number=int(page_number))
    
@permission_required('sales.delete_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff ) 
def deleteOrder(request,pk):
    order = get_object_or_404(Order, pk=pk).delete()
    messages.success(request, "Order has been removed successfully.")
    return redirect('sales:order-list')

@permission_required('sales.delete_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff ) 
def deleteOrderBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            order=Order.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected Orders has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])


class ViewOrder(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name="admin_view/orders/new-order-details.html"
    permission_required = ['sales.view_order']

    def get(self,request,*args,**kwargs):
        order=get_object_or_404(Order,id=kwargs['id'])
        product=ProductVarient.objects.filter(is_available_varient=True)
        settings = Settings.objects.last()
        return super(ViewOrder,self).get(request,settings=settings, order=order,product=product,)

class OrderCreate(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    """Creating custom order of existing products"""
    template_name="admin_view/orders/add_order.html"
    permission_required = ['sales.add_order']

    def get(self,request,*args,**kwargs):
        payment_form = PaymentMethodForm()
        address_form=DeliveryAddressForm()
        deliveryMethod=ShippingMethod.objects.filter(is_active=True)
        shipping_time=ShippingTime.objects.filter(is_active=True)
        addons=ProductAddons.objects.all()
        products=Product.objects.filter(store__is_active=True)
        locations=Location.objects.filter(parent=None,is_active=True)
        try:
            city=locations[0].get_children()[0]
            area=city.get_children()[0]
        except:
            city=''
            area=''
        return super(OrderCreate,self).get(request,products=products,addons=addons,deliveryMethod=deliveryMethod,shipping_time=shipping_time,address_form=address_form,locations=locations,city=city,area=area,payment_form=payment_form)
    
    def post(self,request,*args,**kwargs):
        payment_form = PaymentMethodForm(request.POST)
        address_form=DeliveryAddressForm(request.POST)
        product=request.POST.getlist('varient',None)
        quantity=request.POST.getlist('quantity',None)
        varient=[{'product': product, 'quantity': quantity} for product,quantity in zip(product,quantity)]
        delivery_type=request.POST.get('delivery-type',None)
        delivery_date=request.POST.get('delivery-date',None)
        delivery_time=request.POST.get('delivery-time',None)
        addons_list=[]
        for i,v in enumerate(product):
            addons='addons-'+str(v)
            addon_quantity='addon_quantity-'+str(v)
            addons=request.POST.getlist(addons,None)
            addons_quantity=request.POST.getlist(addon_quantity,None)
            addons=[{'addon': addon, 'quantity': quantity} for addon,quantity in zip(addons,addons_quantity)]
            eggless=request.POST.get('eggless-'+str(v),None)
            sugarless=request.POST.get('sugarless-'+str(v),None)
            message=request.POST.get('message-'+str(v),None)
            image=request.FILES.get('image-'+str(v),None)
            # image1=request.FILES.get('image1-'+str(v),None)
            # image2=request.FILES.get('image2-'+str(v),None)
            # image3=request.FILES.get('image3-'+str(v),None)
            varient[i]['addons']=addons
            varient[i]['eggless']=eggless
            varient[i]['sugarless']=sugarless
            varient[i]['message']=message
            varient[i]['image']=image
            # varient[i]['image1']=image1
            # varient[i]['image2']=image2
            # varient[i]['image3']=image3
                
        if address_form.is_valid() and len(varient)>=1 and payment_form.is_valid():
            payment_method = payment_form.cleaned_data.get('payment_method')
            vendor =payment_form.cleaned_data.get('vendor')
            remarks =payment_form.cleaned_data.get('remarks')
            data=address_form.cleaned_data
            att=address_form.save(commit=False)
            att.receiver_city=Location.objects.filter(id=data.get('receiver_city'))[0].name
            att.save()
            order=createOrder(request,att,varient,message,delivery_type,delivery_date,delivery_time,payment_method,vendor,remarks)
            return redirect('sales:view-order',id=order.id)
        messages.error(request,'Please add some product.')
        deliveryMethod=ShippingMethod.objects.filter(is_active=True)
        shipping_time=ShippingTime.objects.filter(is_active=True)
        addons=ProductAddons.objects.all()
        products=Product.objects.filter(store__is_active=True)
        locations=Location.objects.filter(parent=None,is_active=True)
        try:
            city=locations[0].get_children()[0]
            area=city.get_children()[0]
        except:
            city=''
            area=''
        return super(OrderCreate,self).get(request,products=products,addons=addons,deliveryMethod=deliveryMethod,shipping_time=shipping_time,address_form=address_form,locations=locations,city=city,area=area)

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# @receiver(post_save, sender=OrderItem)
# def send_order_to_odoo(sender, instance, created, **kwargs):
#     try:
#         import requests
#         from accounts.external_api import post_authenticate
#         session_id, tokens, partner_id = post_authenticate()
#         base_url = "https://ohocakes.10orbits-erp.com"
#         url = "/api/account.move"
#         customer = "/api/res.partner"
#         obj = get_object_or_404(OrderItem, id=instance.id)
#         invoice_date = obj.order.created_on
#         name = obj.product.varient_name
#         price = obj.total
#         quantity = obj.quantity
#         order_status = obj.order.order_status
#         payment_source =  obj.order.payment_method
#         reference = obj.order.reference
#         payment_reference = obj.order.order_number
#         # reg_user = obj.order.customer
#         headers = {
#                 "access-token":tokens,
#                 "Content-type":"application/jsonp",
#                 "Cookie":session_id
#             }
#         # if reg_user:
#         #     p_id = reg_user.id
#         # else:
#         vendor = obj.order.vendor
#         if vendor:
#             user_name = obj.order.vendor
#             email = None
#             street = None
#             street2 = None
#             city = None
#         else:
#             user_name = obj.order.delivery_address.receiver_fullname
#             email = obj.order.delivery_address.receiver_email
#             street = obj.order.delivery_address.receiver_delivery_address
#             street2 = obj.order.delivery_address.receiver_landmark
#             city = obj.order.delivery_address.receiver_city

#         post_data = {
#             "name":user_name,
#             "email":email,
#             "street":street,
#             "street2":street2,
#             "city":city
#         }
            
#         post_user = requests.post(base_url+customer,headers=headers, data=json.dumps(post_data, indent=4))
#         datas = post_user.json()
#         p_id = datas['data'][0]['id']
#         api_invoice_line_id = [{'name':name, 'price_unit':price, 'quantity':quantity}]
#         data = {
#             "partner_id":p_id,
#             "invoice_date":str(invoice_date),
#             "move_type":"out_invoice",
#             "__api__invoice_line_ids":str(api_invoice_line_id),
#             "payment_source":payment_source,
#             "source_document": payment_reference,
#             # "payment_reference":reference
#             # "ref":{"order_status":order_status,"payment_status":payment_status, "delivery_status":delivery_status}
#         }
      
#         datas_ = json.dumps(data, indent=4)
#         req = requests.post(base_url+url, headers=headers, data=datas_)
#         if req.status_code == 200:
#             status = "Success"
#         else:
#             status = "Failed"
#         print(status)
#     except Exception as e:
#         print(e)

import pdb
import re
import secrets

def createProduct(data):
    category=Category.objects.get_or_create(name='Custom',is_available=False)
    store=Store.objects.get_or_create(name='custom')
    product=Product.objects.create(name = data.get('name'),
        slug = secrets.token_hex(6),
        store_id = store[0].id, 
        )
    product.category.add(category[0].id)

    if data.get('weight'):
        attribute_value1=AttributeValue.objects.create(attribute=Attribute.objects.get(name='Weight'),
            value=data.get('weight'),
            )
    if data.get('flavour'):
        attribute_value2=AttributeValue.objects.create(attribute=Attribute.objects.get(name='Flavour'),
        value=data.get('flavour'),
        )
    varient=ProductVarient.objects.create(old_price=data.get('price'),
        varient_name=product.name+'-'+str(data.get('weight'))+'-'+str(data.get('flavour')),
        slug=data.get('name').replace(" ", "-")+str(data.get('weight'))+str(data.get('flavour')),
        product_id=product.id,
        quantity=1,
        )
    if data.get('weight'):
        varient.attribut_value.add(attribute_value1)
    if data.get('flavour'):
        varient.attribut_value.add(attribute_value2)
    return {'product':product,'varient':varient}


class CustomOrderCreate(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    """Creating custom order with new product and price"""
    template_name="admin_view/orders/custom_new_order.html"
    permission_required = ['sales.add_order']

    deliveryMethod=ShippingMethod.objects.filter(is_active=True)

    locations=Location.objects.filter(parent=None,is_active=True)
    try:
        city=locations[0].get_children()[0]
        area=city.get_children()[0]
    except:
        city=''
        area=''

    def get(self,request,*args,**kwargs):
        custom_order_formset = CustomOrderFormSet()
        address_form = DeliveryAddressForm()
        payment_form = PaymentMethodForm()
        return super(CustomOrderCreate,self).get(request,deliveryMethod=self.deliveryMethod,address_form=address_form,locations=self.locations,city=self.city,area=self.area,custom_order_formset=custom_order_formset,payment_form=payment_form)
    
    def post(self,request,*args,**kwargs):
        address_form = DeliveryAddressForm(request.POST)        
        delivery_type = request.POST.get('delivery-type',None)
        delivery_date = request.POST.get('delivery-date',None)
        delivery_time = request.POST.get('delivery-time',None)
        payment_form = PaymentMethodForm(request.POST)
        custom_order_formset = CustomOrderFormSet(self.request.POST, self.request.FILES)
        shipping_cost=0 
        addon_price_total=0
        total=0
        if address_form.is_valid() and custom_order_formset.is_valid() and payment_form.is_valid():
            payment_order_data = payment_form.cleaned_data
            payment_method = payment_order_data.get('payment_method')
            vendor = payment_order_data.get('vendor')
            remarks = payment_order_data.get('remarks')
            data=address_form.cleaned_data
            att=address_form.save(commit=False)
            att.receiver_city=Location.objects.filter(id=data.get('receiver_city'))[0].name
            att.save()
            product = []
            for form in custom_order_formset:
                if form.is_valid():
                    data=form.cleaned_data
                    shipping_cost = shipping_cost+get_object_or_404(ShippingMethod,id=delivery_type).price*1 #1 is quantity and constant here
                    total = total + data.get('price')
                    for i in data.get('addons'):
                        addon_price_total=addon_price_total + i.price#ProductAddons.objects.get(id=i).price
                    # if form.is_valid():
                    #     data=form.cleaned_data
                    prod=createProduct(data)
                    product.append(prod.get('varient'))

            sub_total=total+addon_price_total
            total=sub_total+shipping_cost
            order=createCustomOrder(request,att,custom_order_formset,delivery_type,delivery_date,delivery_time,shipping_cost,total,sub_total,payment_method,product,vendor,remarks)
            return redirect('sales:view-order',id=order.id)
        return super(CustomOrderCreate,self).get(request,deliveryMethod=self.deliveryMethod,address_form=address_form,locations=self.locations,city=self.city,area=self.area,custom_order_formset=custom_order_formset,payment_form=payment_form)



class OrderUpdate(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    """Updating order"""
    template_name="admin_view/orders/edit_order.html"
    permission_required = ['sales.change_order']

    def get(self,request,*args,**kwargs):
        order=get_object_or_404(Order,id=self.kwargs['id'])
        payment_form = PaymentMethodForm(initial = {'payment_method':order.payment_method,'vendor':order.vendor,'remarks':order.remarks})
        delivery_address=get_object_or_404(DeliveryAddress,id=order.delivery_address.id)
        address_form=DeliveryAddressForm(instance=delivery_address)
        deliveryMethod=ShippingMethod.objects.filter(is_active=True)
        shipping_time=ShippingTime.objects.filter(is_active=True)
        addons=ProductAddons.objects.all()
        products=Product.objects.filter(store__is_active=True)
        locations=Location.objects.filter(parent=None,is_active=True)
        return super(OrderUpdate,self).get(request,order=order,products=products,addons=addons,deliveryMethod=deliveryMethod,shipping_time=shipping_time,address_form=address_form,locations=locations,payment_form=payment_form)
    
    def post(self,request,*args,**kwargs):
        order=get_object_or_404(Order,id=self.kwargs['id'])
        payment_form = PaymentMethodForm(request.POST)
        delivery_address=get_object_or_404(DeliveryAddress,id=order.delivery_address.id)
        address_form=DeliveryAddressForm(request.POST,instance=delivery_address)
        product=request.POST.getlist('varient',None)
        quantity=request.POST.getlist('quantity',None)
        varient=[{'product': product, 'quantity': quantity} for product,quantity in zip(product,quantity)]
        delivery_type=request.POST.get('delivery-type',None)
        delivery_date=request.POST.get('delivery-date',None)
        delivery_time=request.POST.get('delivery-time',None)
        addons_list=[]
        for i,v in enumerate(product):
            addons='addons-'+str(v)
            addon_quantity='addon_quantity-'+str(v)
            addons=request.POST.getlist(addons,None)
            addons_quantity=request.POST.getlist(addon_quantity,None)
            addons=[{'addon': addon, 'quantity': quantity} for addon,quantity in zip(addons,addons_quantity)]
            eggless=request.POST.get('eggless-'+str(v),None)
            sugarless=request.POST.get('sugarless-'+str(v),None)
            message=request.POST.get('message-'+str(v),None)
            image=request.FILES.get('image-'+str(v),None)
            image1=request.FILES.get('image1-'+str(v),None)
            image2=request.FILES.get('image2-'+str(v),None)
            image3=request.FILES.get('image3-'+str(v),None)
            varient[i]['addons']=addons
            varient[i]['eggless']=eggless
            varient[i]['sugarless']=sugarless
            varient[i]['message']=message
            varient[i]['image']=image
            varient[i]['image1']=image1
            varient[i]['image2']=image2
            varient[i]['image3']=image3
                
        if address_form.is_valid() and len(varient)>=1 and payment_form.is_valid():
            from .utility import createLog
            createLog(request,order)
            payment_method = payment_form.cleaned_data.get('payment_method')
            vendor = payment_form.cleaned_data.get('vendor')
            remarks = payment_form.cleaned_data.get('remarks')
            data=address_form.cleaned_data
            att=address_form.save(commit=False)
            att.receiver_city=data.get('receiver_city')#Location.objects.filter(id=data.get('receiver_city'))[0].name
            att.save()
            try:
                order=updateOrder(request,att,varient,message,delivery_type,delivery_date,delivery_time,order,payment_method,vendor,remarks)
            except:
                pass
            return redirect('sales:view-order',id=order.id)
        messages.error(request,'Please add some product or completely delete product.')
        deliveryMethod=ShippingMethod.objects.filter(is_active=True)
        shipping_time=ShippingTime.objects.filter(is_active=True)
        addons=ProductAddons.objects.all()
        products=Product.objects.filter(store__is_active=True)
        locations=Location.objects.filter(parent=None,is_active=True)
        return super(OrderUpdate,self).get(request,products=products,addons=addons,deliveryMethod=deliveryMethod,shipping_time=shipping_time,address_form=address_form,locations=locations,order=order)

def recalculateOrder(request,order,order_item,price,total_price):
    from .utility import createLog
    createLog(request,order)
    order_item.total=total_price
    order_item.sub_total=total_price
    order_item.price=price
    order_item.save()
    total = 0
    for i in order.items.all():
        total=total+i.total
    order.sub_total_order = total
    total = total+order.shipping_cost
    order.total=total
    order.updated_by=request.user
    order.save()

@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def customOrderPriceUpdate(request):
    order = request.GET.get('order')
    order_item = request.GET.get('order_item')
    price = request.GET.get('price')
    # if order.store == 'custom':
    order = get_object_or_404(Order,id =order)
    order_item = get_object_or_404(OrderItem,id=order_item,order=order)
    ProductVarient.objects.filter(id=order_item.product.id).update(old_price=price)
    addons = order_item.orderitem_addons.all()
    
    addon_total=0
    for i in addons:
        addon_total=addon_total+i.price
    total_price = float(addon_total)+float(price)
    
    recalculateOrder(request,order,order_item,price,total_price)
    return JsonResponse({'status':'Success'})
    # return JsonResponse({'error':'Unable to change'})

@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def customOrderFlavourUpdate(request):
    from .utility import createLog
    createLog(request,order)
    order = request.GET.get('order')
    order = get_object_or_404(Order,id=order)
    order.updated_by = request.user
    order.save()
    order_item = request.GET.get('order_item')
    flavour = request.GET.get('flavour')
    item = get_object_or_404(OrderItem,id=order_item)
    name = item.product.product.name+'-'+str(item.pound)+'-'+str(flavour)
    OrderItem.objects.filter(id=order_item).update(name=name,flavour = flavour)
    return JsonResponse({'status':'Success'})

@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def customOrderPoundUpdate(request):
    from .utility import createLog
    createLog(request,order)
    order = request.GET.get('order')
    order = get_object_or_404(Order,id=order)
    order.updated_by = request.user
    order.save()
    order_item = request.GET.get('order_item')
    pound = request.GET.get('pound')
    item = get_object_or_404(OrderItem,id=order_item)
    name = item.product.product.name+'-'+str(pound)+'-'+item.flavour
    OrderItem.objects.filter(id=order_item).update(name=name, pound = pound)
    return JsonResponse({'status':'Success'})

class CustomOrderUpdate(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    """Creating custom order with new product and price"""
    template_name="admin_view/orders/custom_new_order_update.html"
    permission_required = ['sales.change_order']

    deliveryMethod=ShippingMethod.objects.filter(is_active=True)
    locations=Location.objects.filter(parent=None,is_active=True)
    try:
        city=locations[0].get_children()[0]
        area=city.get_children()[0]
    except:
        city=''
        area=''

    def get(self,request,*args,**kwargs):
        pass
        # order = get_object_or_404(Order,id=self.kwargs['pk'])
        # initial = []
        # data = {}
        # for i in order.items.all():
        #     try:
        #         flav = i.product.attribut_value.all()[1].value
        #     except:
        #         flav = None
        #     data['name']=i.product.product.name
        #     data['weight']=i.product.attribut_value.all()[0].value
        #     data['flavour']= flav
        #     data['price']=i.product.old_price
        #     data['addons']=[j.id for j in i.orderitem_addons.all()]
        #     data['is_eggless']=i.is_eggless
        #     data['is_sugarless']=i.is_sugerless
        #     data['image']=i.photo_cake_image
        #     data['message']=i.special_instruction
        #     initial.append(data)
        
        # custom_order_formset = CustomOrderFormSet(initial=initial)
        # address_form = DeliveryAddressForm(instance = order.delivery_address)
        # payment_form = PaymentMethodForm(initial = {'payment_method':order.payment_method})
        # return super(CustomOrderUpdate,self).get(request,deliveryMethod=self.deliveryMethod,address_form=address_form,locations=self.locations,city=self.city,area=self.area,custom_order_formset=custom_order_formset,payment_form=payment_form,order=order)
    
    # def post(self,request,*args,**kwargs):
    #     address_form = DeliveryAddressForm(request.POST)        
    #     delivery_type = request.POST.get('delivery-type',None)
    #     delivery_date = request.POST.get('delivery-date',None)
    #     delivery_time = request.POST.get('delivery-time',None)
    #     payment_form = PaymentMethodForm(request.POST)
    #     custom_order_formset = CustomOrderFormSet(self.request.POST, self.request.FILES)
    #     shipping_cost=0 
    #     addon_price_total=0
    #     total=0
    #     if address_form.is_valid() and custom_order_formset.is_valid() and payment_form.is_valid():
    #         payment_method = payment_form.cleaned_data.get('payment_method')
    #         data=address_form.cleaned_data
    #         att=address_form.save(commit=False)
    #         att.receiver_city=Location.objects.filter(id=data.get('receiver_city'))[0].name
    #         att.save()
    #         product = []
    #         for form in custom_order_formset:
    #             if form.is_valid():
    #                 data=form.cleaned_data
    #                 shipping_cost = shipping_cost+get_object_or_404(ShippingMethod,id=delivery_type).price*1 #1 is quantity and constant here
    #                 total = total + data.get('price')
    #                 for i in data.get('addons'):
    #                     addon_price_total=addon_price_total + i.price#ProductAddons.objects.get(id=i).price
    #                 if form.is_valid():
    #                     data=form.cleaned_data
    #                     prod=createProduct(data)
    #                     product.append(prod.get('varient'))

    #         sub_total=total+addon_price_total
    #         total=sub_total+shipping_cost
    #         order=createCustomOrder(att,custom_order_formset,delivery_type,delivery_date,delivery_time,shipping_cost,total,sub_total,payment_method,product)
    #         return redirect('sales:view-order',id=order.id)
    #     return super(CustomOrderCreate,self).get(request,deliveryMethod=self.deliveryMethod,address_form=address_form,locations=self.locations,city=self.city,area=self.area,custom_order_formset=custom_order_formset,payment_form=payment_form)


def getVarientList(request):
    if request.method=='GET':
        product_id=request.GET.get('product',None)
        varient=list(ProductVarient.objects.filter(product=product_id).values('id','varient_name'))
        return JsonResponse({'status':'Success','varient':varient})

def getVarient(request):
    if request.method=='GET':
        varient_id=request.GET.get('varient',None)
        var=ProductVarient.objects.filter(id=varient_id).prefetch_related('product')
        store=var[0].product.store.name
        eggless_price=var[0].product.store.eggless_price
        sugarless_price=var[0].product.store.sugar_less_price
        selling_price=var[0].selling_price
        varient=list(ProductVarient.objects.filter(id=varient_id).values('id','varient_name',))
        varient[0]['store']=store
        varient[0]['price']=selling_price
        varient[0]['eggless_price']=eggless_price
        varient[0]['sugarless_price']=sugarless_price
        varient[0]['url']=var[0].product.get_absolute_url()
        varient[0]['addons']=list(ProductAddons.objects.all().values('id','name','price'))
        return JsonResponse({'status':'Success','varient':varient})

def getAddons(request):
    if request.method=='GET':
        addon=request.GET.get('addon')
        addon=list(ProductAddons.objects.filter(id=addon).values('id','name','price'))
        return JsonResponse({'status':'Success','addon':addon})
def getTime(request):
    if request.method=='GET':
        delivery_type=request.GET.get('delivery_type')
        time=list(ShippingTime.objects.filter(shipping_time__id=delivery_type).values('id','time_from','time_to'))
        return JsonResponse({'status':'Success','time':time})

class OrderInvoice(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name="admin_view/orders/order-invoice.html"
    permission_required = ['sales.change_order']
    def get(self,request,*args,**kwargs):
        order=get_object_or_404(Order,id=kwargs['id'])
        product=ProductVarient.objects.filter(is_available_varient=True)
        settings = Settings.objects.last()
        return super(OrderInvoice,self).get(request,settings=settings, order=order,product=product)

@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderStatusUpdate(request):
    status = request.GET.get('order_status', None)
    order_id = request.GET.get('order_number', None)
    remarks = request.GET.get('remarks',None)
    user = request.user.id
    order_obj = Order.update_order_status(order_id,status,remarks)
    unconfirmed_count = Order.objects.filter(order_status="Unconfirmed").count() 
    error = "None"
    order_pass = ""
    try:
        if status == "Processing" or status == "Confirmed" or status == "Complete" or status=="Dispatched":
            order__ = Order.objects.filter(id=order_id).values('order_number')
            order_num = order__[0].get('order_number')
            rider = OrderDelivery.objects.filter(order__order_number=order_num).values('user__username', 'user__profile__phone_number', 'user__email')
            if rider:
                rider_name = rider[0].get('user__username')
                rider_phone = rider[0].get('user__profile__phone_number')
                rider_email = rider[0].get('user__email')
            else:
                rider_name = None
                rider_phone = None
                rider_email = None
            
            order_pass, error = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, request.user.username,request.user.email)
            if order_pass == 'Success' or order_pass == 'Failed':
                Order.objects.filter(id=order_id).update(odoo_status=order_pass)
            else:
                pass
        else:
            pass
    except Exception as e:
        print(e, "this is error")
    return JsonResponse({'data':200,'status':status,'id':order_id,'unconfirmed_count':unconfirmed_count, "odoo_status":order_pass, "error":error})


@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def send_email_order_status(request):
    order_number = request.GET.get('order_number',None)
    status = request.GET.get('status',None)
    order=Order.objects.get(id=order_number)
    baseurl = hostname_from_request(request)
    send_emails_on_item_process(order)
    return JsonResponse({})

"""Update payment status of order"""
@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def paymentStatusUpdate(request):
    status = request.GET.get('payment_status', None)
    order_id = request.GET.get('order_number', None)
    Order.objects.filter(id=order_id).update(payment_status=status)
    return JsonResponse({'data':200,'status':status})


"""Changing Delivery Status of order"""
@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deliveryStatusUpdate(request):
    status = request.GET.get('delivery_status', None)
    order_id = request.GET.get('order_id', None)
    Order.objects.filter(id=order_id).update(delivery_status=status)
    return JsonResponse({'data':200,'status':status})



"""Incomplete now"""
@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderItemUpdate(request):
    if request.method=='POST':
        counter=request.POST.get('counter',None)
        order=request.POST.get('order',None)
        messages.success(request, "Order items has been saved successfully.")
    return redirect(request.META['HTTP_REFERER'])

"""Incomplete now"""
@permission_required('sales.delete_orderitem',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteOrderItem(request,pk):
    if request.method=='POST':
        order_id=request.POST.get('order',None)
        item = get_object_or_404(OrderItem, pk=pk).delete()
        order_items = OrderItem.objects.filter(order = order_id)
        try:
            order=Order.objects.get(id=order_id)
        except:
            raise Http404
        order_items_total = 0
        for item in order_items:
            order_items_total =  order_items_total + item.total
        grand_total = total_with_taxes + order.shipping_cost
        Order.objects.filter(id = order_id).update(total=grand_total,sub_total_order=order_items_total)
        messages.success(request, "Order Item has been removed successfully.")
        return redirect(request.META['HTTP_REFERER'])

from .utility import *
"""Incomplete now"""
@permission_required('sales.add_orderitem',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderItemCreate(request):
    if request.method=='POST':
        product=request.POST.get('product')
        quantity=request.POST.get('quantity')
        order_id=request.POST.get('order')
        try:
            product=ProductVarient.objects.get(id=product)
            order=Order.objects.get(id=order_id)
            price= product.selling_price
        except:
            raise Http404
        if int(product.quantity) >= int(quantity):
            order_item_total_price = int(price)*int(quantity)
            order_item = OrderItem.objects.create(order= order,product=product,quantity=quantity,price=price,total=order_item_total_price,sub_total= order_item_total_price)

            items = OrderItem.objects.filter(order=order)
            all_order_item_total = 0
            for single_item in items:
                all_order_item_total = all_order_item_total+ single_item.total

            total_grand= order.shipping_cost + total_with_taxes
            Order.objects.filter(id= order_id).update(total=total_grand, sub_total_order= all_order_item_total)

            _quantity=product.quantity-int(quantity)
            ProductVarient.objects.filter(id=product.id).update(quantity=_quantity)
            messages.success(request, "Order Item has been added successfully.")
        else:
            messages.error(request, "Quantity exceeds available stock")
        return redirect(request.META['HTTP_REFERER'])



@permission_required('sales.change_orderitem',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def update_order_item_quantity(request):
    quantity= request.GET.get('quantity',None)
    order_item_id= request.GET.get('order_item_id',None)
    order_id = request.GET.get('order_id',None)
    
    order = Order.objects.get(id=order_id)
    order_item = OrderItem.objects.get(id=order_item_id)
    shipping_cost=int(quantity) * (order_item.shipping_method.price)
    
    sub_total_price=int(quantity) * (order_item.price)
    total_price = int(quantity) * (order_item.price)+shipping_cost
    order_item.quantity = int(quantity) 
    order_item.total = total_price
    order_item.sub_total = sub_total_price
    order_item.shipping_cost=shipping_cost
    order_item.save()

    items = OrderItem.objects.filter(order=order)
    all_order_item_total = 0
    all_order_item_total_shipping_cost=0
    for single_item in items:
        all_order_item_total = all_order_item_total+ single_item.total
        all_order_item_total_shipping_cost=all_order_item_total_shipping_cost+(single_item.shipping_method.price*int(quantity))

    total_grand= all_order_item_total_shipping_cost + all_order_item_total

    if order.coupon:
        all_order_item_total=all_order_item_total-order.discount
        total_grand=total_grand-order.discount

    Order.objects.filter(id= order_id).update(total=total_grand, sub_total_order= all_order_item_total,shipping_cost=all_order_item_total_shipping_cost)
    return JsonResponse({'message':'success'})


"""Return date of today"""
def today__date():
    from datetime import date as d
    today = d.today()
    return today


"""Delivery Board kanban listing"""
class DeliveryBoard(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    from datetime import timedelta
    permission_required = ['sales.change_order','sales.add_order','sales.view_order','sales.delete_order','sales.change_orderdelivery','sales.add_orderdelivery','sales.view_orderdelivery','sales.delete_orderdelivery']
    template_name='admin_view/orders/delivery-status.html'

    def get(self,request,*args,**kwargs):
        delivery_form=AssignDeliveryForm()
        date_filter_order = request.GET.get('date_filter_order',None)
        day=self.kwargs['day']
        if day=='today':
            date=today__date()
        if day=='tomorrow':
            date=today__date()+timedelta(days=1)
        if day=='this_week':
            date=today__date()+timedelta(days=7)
        if day == 'all':
            date=today__date()
        selected_store_slug=self.request.GET.get('store',None)
        try:
            store=Store.objects.get(slug=selected_store_slug)
        except:
            store=None
        try:
            factory = Factories.objects.all()
            factory_list = []
            for i in factory:
                if store:
                    if day=='this_week':
                        order_count = Order.objects.filter(date__gte=today__date(),items__product__product__store__slug=store.slug, delivery_order__factory__id=i.id).count()
                    elif day == 'all':
                        if date_filter_order:
                            order_count = Order.objects.filter(date=date_filter_order,items__product__product__store__slug=store.slug, delivery_order__factory__id=i.id).count()
                        else:
                            order_count = Order.objects.filter(date__gte=today__date(),items__product__product__store__slug=store.slug, delivery_order__factory__id=i.id).count()
                    else:
                        order_count = Order.objects.filter(date=today__date(),items__product__product__store__slug=store.slug, delivery_order__factory__id=i.id).count()
                else:
                    if day == 'this_week':
                        order_count=Order.objects.filter(date__gte=today__date(), delivery_order__factory__id=i.id).count()
                    elif day == 'all':
                        if date_filter_order:
                            order_count=Order.objects.filter(date=date_filter_order, delivery_order__factory__id=i.id).count()
                        else:
                            order_count=Order.objects.filter(date__gte=today__date(), delivery_order__factory__id=i.id).count()
                    else:
                        order_count=Order.objects.filter(date=today__date(), delivery_order__factory__id=i.id).count()
                data = {}
                data["factory_name"] = i.name
                data["order_count"] = order_count
                factory_list.append(data)
        except Exception as e:
            factory_list = []

        order_alert_data = OrderAlert.distinct_order(day, date)
        available_store=Store.objects.filter(is_active=True)
        today_date=today__date()
        pending_order_items=Order.get_pending_order_items(date,store,day,date_filter_order)
        dispatched_order_items=Order.get_dispatched_order_items(date,store,day,date_filter_order)
        processing_order_items=Order.get_processing_order_items(date,store,day,date_filter_order)
        complete_order_items=Order.get_complete_order_items(date,store,day,date_filter_order)
        confirmed_order_items=Order.get_confirmed_order_items(date,store,day,date_filter_order)
        cancelled_order_items=Order.get_cancelled_order_items(date,store,day,date_filter_order)
        return super(DeliveryBoard,self).get(request,selected_store_slug=selected_store_slug,available_store=available_store, \
          date=date, pending_order_items=pending_order_items,complete_order_items=complete_order_items, \
        processing_order_items=processing_order_items,day=day,confirmed_order_items=confirmed_order_items, \
        delivery_form=delivery_form,dispatched_order_items = dispatched_order_items,date_filter_order=date_filter_order, \
        order_alert_data=order_alert_data,cancelled_order_items=cancelled_order_items, factory_list=factory_list)

"""Get all the assigned deliveries order"""
@permission_required('sales.view_orderdelivery',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderAssignedToDeliveryBoy(request):
    if request.method=='GET':
        order_keyword=request.GET.get('order_keyword',None)
        print(order_keyword)
        delivery_form=AssignDeliveryForm()
        order_assigned=OrderDelivery.objects.all().order_by('-id')[:400]
        if order_keyword:
            order_assigned=OrderDelivery.objects.filter(Q(user__first_name=order_keyword)|
                Q(user__email=order_keyword)|
                Q(order__order_number=order_keyword)
                ).order_by('-id')

        paginator = Paginator(order_assigned, 50)
        try:
           page = request.GET.get('page')
           qs = paginator.get_page(page)
        except PageNotAnInteger:
           qs = paginator.get_page(1)
        except EmptyPage:
           qs = paginator.get_page(paginator.num_pages)

        return render(request,'admin_view/orders/order_item_assigned_to_delivery_boy.html',{'order_assigned':qs,'delivery_form':delivery_form,'order_keyword':order_keyword})


"""Create order to be delivered with pickup time,date and assign delivery boy"""
# @permission_required('sales.add_orderdelivery',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
def assignDeliveryBoy(request):
    if request.method=='POST':
        form=AssignDeliveryForm(request.POST)
        date=request.POST.get('pickup_date',None)
        time=request.POST.get('pickup_time',None)
        expected_delivery_time=request.POST.get('expected_delivery_time',None)
        user = request.POST.get('user')
        factory = request.POST.get('factory', None)
        if not time or not date:
            return JsonResponse({'error':'Please select time and date.'})
        order_id=request.POST.get('order',None)
        order=get_object_or_404(Order,id=order_id)
        store=order.store
        odoo = "Failed"
        error = "None"
        try:
            if OrderDelivery.objects.filter(order=order).exists():
                if factory and user:
                    OrderDelivery.objects.filter(order=order).update(
                    user=get_object_or_404(User, id=user),
                    factory=get_object_or_404(Factories, id=factory),
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
                if user and not factory:
                    OrderDelivery.objects.filter(order=order).update(
                    user=get_object_or_404(User, id=user),
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
                if not user and factory:
                    OrderDelivery.objects.filter(order=order).update(
                    factory=get_object_or_404(Factories, id=factory),
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
                else:
                    OrderDelivery.objects.filter(order=order).update(
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
            else:
                if not factory and user:
                    OrderDelivery.objects.create(
                    user=get_object_or_404(User, id=user),
                    order=order,
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
                elif not user and not factory:
                    OrderDelivery.objects.create(
                    order=order,
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
                elif factory and not user:
                    OrderDelivery.objects.create(
                    order=order,
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    factory=get_object_or_404(Factories, id=factory),
                    )
                else:
                    OrderDelivery.objects.create(
                    user=get_object_or_404(User, id=user),
                    order=order,
                    factory=get_object_or_404(Factories, id=factory),
                    pickup_time=time,
                    pickup_date=date,
                    expected_delivery_time=expected_delivery_time,
                    store=store,
                    )
            try:
                rider = OrderDelivery.objects.filter(order__id=order_id).values('user__username', 'user__profile__phone_number', 'user__email')
                if rider:
                    rider_name = rider[0].get('user__username')
                    rider_phone = rider[0].get('user__profile__phone_number')
                    rider_email = rider[0].get('user__email')
                else:
                    rider_name = None
                    rider_phone = None
                    rider_email = None
                odoo, error = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, request.user.username,request.user.email)
                Order.objects.filter(id=order_id).update(odoo_status=odoo)
            except Exception as e:
                print(e)
            return JsonResponse({'status':200,'order_number':order.order_number, "odoo_status":odoo, "odo_error":error})
        except Exception as e:
            print(e, "error on somewhere")
            return JsonResponse({'status':400, 'error':'Select time again.'+str(e)})


@permission_required('sales.delete_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff ) 
def deleteOrderAssigned(request,pk):
    order = get_object_or_404(OrderDelivery, pk=pk).delete()
    messages.success(request, "Order assigned has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])



@permission_required('sales.delete_orderdelivery',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deliveryAssignBulkDelete(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        print(item_id)
        for i in range(0,len(item_id)):
            order=OrderDelivery.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected Assigned Orders has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])


"""Check order status to allow operator assign delivery boy at processing and pickup date and time at confirmed"""
@permission_required('sales.view_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def checkOrderStatus(request):
    if request.method=='GET':
        orderId=request.GET.get('order_id',None)
        order=Order.objects.get(id=orderId)
        try:
            pickup_date=order.delivery_order.pickup_date
            pickup_time=order.delivery_order.pickup_time
            delivery_boy=order.delivery_order.user.id if order.delivery_order.user else None
            expected_delivery_time = order.delivery_order.expected_delivery_time
        except:
            from datetime import date
            pickup_date=date.today()
            pickup_time=None
            delivery_boy=None
            expected_delivery_time = None
        try:
            factory = order.delivery_order.factory.id if order.delivery_order.factory else None
        except:
            factory =None
        data={'order_status':order.order_status,'pickup_date':pickup_date,'pickup_time':pickup_time,'delivery_boy':delivery_boy,'customer_delivery_date':order.date,'time_from':order.time.time_from,'time_to':order.time.time_to,'factory':factory,'expected_delivery_time':expected_delivery_time}
        return JsonResponse(data)


"""Order status change from delivery board kanban"""
@permission_required('sales.change_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateOrderStatus(request):
    if request.method=='GET':
        orderId=request.GET.get('order_number',None)
        status=request.GET.get('status',None).title()
        available_status=['Confirmed','Unconfirmed','Processing','Dispatched','Complete','Cancelled']
        if status in available_status:
            order_id=get_object_or_404(Order,order_number=orderId).id
            Order.update_order_status(order_id,status,remarks=None)
            # Order.objects.filter(order_number=orderId).update(order_status=status)
            order=get_object_or_404(Order,order_number=orderId)
            send_emails_on_item_process(order)
            return JsonResponse({'status':'success','order_status':status,'order_id':orderId})
        else:
            return JsonResponse({'error':'Some thing went wrong.'})

"""Send email to client on order status change"""
def send_emails_on_item_process(order):
    sender_email=order.delivery_address.sender_email
    status=order.order_status
    # try:
    setting=Settings.objects.first()
    currency = setting.currency
    if status=='Complete':
        send_email_to_user(subject_name="Your order has been completed",to_email=str(sender_email),obj={'order':order,'setting':setting,'currency':currency,},template_location="email_templates/order_delivered.html")
    if status=='Confirmed':
        send_email_to_user(subject_name="Your order has been confirmed",to_email=str(sender_email),obj={'order':order,'setting':setting,'currency':currency,},template_location="email_templates/order_confirmed.html")
    if status=='Processing':
        send_email_to_user(subject_name="Your order has been processed",to_email=str(sender_email),obj={'order':order,'setting':setting,'currency':currency,},template_location="email_templates/order_dispatched.html")
    # except Exception as e:
    #     pass



    


"""For displaying order Summery of each order at delivery board"""
from sales.api.serializers import OrderDetailSerializer
@permission_required('sales.view_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderDetail(request):
    if request.method=='GET':
        orderId=request.GET.get('order_id',None)
        queryset=Order.objects.filter(id=orderId)
        serializer=OrderDetailSerializer(queryset,many=True)
        return JsonResponse(serializer.data,safe=False)

@permission_required('sales.view_order',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def latestOrder(request):
    if request.method == 'GET':
        current_total=request.GET.get('current_total',None)
        total_unconfirmed=Order.objects.filter(order_status='Unconfirmed').count()
        new_item_count=int(total_unconfirmed)-int(current_total)
        return JsonResponse({'status':'success','new_item_count':new_item_count,'total_unconfirmed':total_unconfirmed})



'''
Sales and Order report View
'''

from sales.sales_callback import *
class SalesOverTimeView(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name="admin_view/sales/sales_order_report/sales_over_time.html"
    permission_required = ['sales.change_order']
    # import datetime

    def get(self, request, *arge, **kwargs):
        date__range=self.request.GET.get('date_range',None)
        order_status = self.request.GET.get('order_status',None)
        time_range = self.request.GET.get('time_range', None)


        context = {
            'date_range': date__range,
            'order_status':order_status,
            'time_range':time_range,
            
        }
        new_list=[]
        if date__range or order_status or time_range: #or year or month:
            if order_status is not None and time_range:
                if order_status=='month' and time_range == 'daily':
                    current_month = date.today().month
                    current_year= date.today().year
                    from calendar import monthrange
                    num_days = monthrange(current_year, current_month)[1]
                    
                    total_sells = 0
                    for i in range(1, num_days+1):
                        get_date = datetime.strptime(f'{current_year}-{current_month}-{i}', '%Y-%m-%d').date()
                        data = sells_over_time_filter_date_range(get_date)
                        total_sells += data['total']
                        data.update({'status':get_date})
                        new_list.append(data)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                

                elif order_status == 'year' and time_range == 'daily':
                    # import datetime
                    current_year= date.today().year
                    start_date = datetime.strptime(f'{current_year}-{1}-{1}', '%Y-%m-%d').date()
                    end_date= datetime.strptime(f'{current_year}-{12}-{30}', '%Y-%m-%d').date()
                    date_list = date_range(start_date, end_date)
                    p = Paginator(date_list, 10)
                    page_number = request.GET.get('page')
                    if page_number == None:
                        page_number=1
                    try:
                        page_obj = p.get_page(page_number)
                    except PageNotAnInteger:
                        page_obj = p.page(1)
                    except EmptyPage:
                        page_obj = p.page(p.num_pages)
                    total_sells = 0
                    for _date_ in page_obj:
                        data = sells_over_time_filter_date_range(_date_)
                        total_sells += data['total']
                        data.update({'status':_date_})
                        new_list.append(data)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context,'date_range':date__range, 'order_status':order_status, 'time_range':time_range, 'page_obj':page_obj, 'page_number':int(page_number)})
                    
                elif order_status=='month' and time_range=='weekly':
                    year= date.today().year
                    month = date.today().month
                    week = week_from_date(date(year, month, 1))
                    only_week_ = list(week)[1]
                    week_list_of_month = [only_week_, only_week_+1,only_week_+2,only_week_+3,only_week_+4]
                    i=1
                    for weeks in week_list_of_month:
                        data = sells_over_time_week_month_and_yearly_basis(weeks, month, year)
                        status = (f'{year}/{month}/Week-{i}')
                        data.update({'status':status})
                        new_list.append(data)
                        i+=1
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                    
                elif order_status == 'week' and time_range == 'daily':
                    date_ = timezone.now().isocalendar()[1]
                    year= date.today().year
                    day_list = weeknum_to_dates(date_, year)
                    total_sells = 0
                    for day in day_list:
                        data = sells_over_time_filter_date_range(day)
                        total_sells += data['total']
                        data.update({'status':day})
                        new_list.append(data)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    

                elif order_status == 'year' and time_range=='weekly':
                    year= date.today().year
                    month = date.today().month
                    for j in range(1,53):
                        data = sells_over_time_week_month_and_yearly_basis(j, month, year)
                        status = (f'{year}-Week-{j}')
                        data.update({'status':status})
                        new_list.append(data)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                    
                elif order_status == 'year' and time_range == 'monthly':
                    month_list = [1,2,3,4,5,6,7,8,9,10,11,12]
                    current_year= date.today().year

                    for months in month_list:
                        data_retrive = sells_over_time_month_and_yearly_basis(months, current_year)
                        status = datetime.strptime(f'{current_year}-{months}', '%Y-%m').date()
                        data_retrive.update({'status':status})
                        new_list.append(data_retrive)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
            if order_status and not time_range and not date__range:
                if order_status == 'today':
                    date_ = timezone.now()
                    new_list= Order.sells_over_time(date_)
                    new_list[0].update({'status':order_status})
                
                elif order_status.strip(' ') == 'yesterday':
                    date_ = (timezone.now() - timedelta(1)).strftime('%Y-%m-%d')
                    new_list = Order.sells_over_time(date_)
                    new_list[0].update({'status':order_status})
                    
                elif order_status == 'week':
                    date_ = timezone.now().isocalendar()[1]
                    new_list = Order.sells_over_time_week(date_)
                    new_list[0].update({'status':'This Week'})

                elif order_status == 'month':
                    date_ = timezone.now().month
                    new_list = Order.sells_over_time_month(date_)
                    new_list[0].update({'status':'This Month'})

                elif order_status == 'year':
                    date_ = timezone.now().year
                    new_list = Order.sells_over_time_year(date_)
                    new_list[0].update({'status':f'In {date_}'})
                return render(request, self.template_name, {'new_list':new_list, 'context':context})

            if  date__range and time_range:
                if len(date__range)>1:
                    date__range=date__range.split('to')
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    date_range_req = f'{start_date}+to+{end_date}'
                    if time_range == 'daily':
                        date_list = date_range(start_date, end_date)
                        p = Paginator(date_list, 20)
                        page_number = request.GET.get('page')
                        if page_number == None:
                            page_number=1
                        try:
                            page_obj = p.get_page(page_number)
                        except PageNotAnInteger:
                            page_obj = p.page(1)
                        except EmptyPage:
                            page_obj = p.page(p.num_pages)
                        total_sells = 0
                        for _date_ in page_obj:
                            data = sells_over_time_filter_date_range(_date_)
                            total_sells += data['total']
                            data.update({'status':_date_})
                            new_list.append(data)
                        return render(request, self.template_name, {'new_list':new_list, 'context':context, 'order_status':order_status, 'date_range':date_range_req, 'time_range':time_range, 'page_obj':page_obj, 'page_number':int(page_number)})
                    

                    elif time_range == 'weekly':
                        week_list = find_weeks(start_date, end_date)
                        total_sells = 0
                        i=0
                        j=7
                        for week in week_list:
                            data = sells_over_time_filter_week(week[-2:])
                            data.update({'status':f'{start_date+datetime.timedelta(days=i)} to {start_date+datetime.timedelta(days=j)}'})
                            new_list.append(data)
                            i+=7
                            j+=7
                    
                    elif time_range == 'monthly':
                        months = calculate_all_month_in_year_range(start_date, end_date)
                        for month in months:
                            month_, year = month.split('-')
                            data = sells_over_time_month_and_yearly_basis(month_, year)
                            data.update({'status':f'{year}-{month_}'})
                            new_list.append(data)

                    elif time_range == 'yearly':
                        start_year = start_date.year
                        end_year = end_date.year
                        diff = end_year-start_year
                        year_list = []
                        if diff !=0:
                            num_year = diff
                            for i in range(num_year+1):
                                years = start_year+i
                                year_list.append(years)
                            total_sells=0
                            for year in year_list:
                                data = sells_over_time_yearly_basis(year)
                                total_sells += data['total']
                                data.update({'status':f'In Year {year}'})
                                new_list.append(data)

                        else:
                            data = sells_over_time_yearly_basis(start_year)
                            total_sells = data['total']
                            data.update({'status':f'In Year {start_year}'})
                            new_list.append(data)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                else:
                    start = date__range[0].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_range_on_date(start_date)
                    return render(request, self.template_name, {'new_list':new_list, 'context':context})

            if date__range:
                date__range=date__range.split('to')
                if len(date__range)>1:
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_date_range(start_date, end_date)
                    
                else:
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_range_on_date(start_date) 

                return render(request, self.template_name, {'new_list':new_list, 'context':context})
            return render(request, self.template_name)
                
        else:
            get_date = Order.objects.order_by('-placed_on').values_list('placed_on').distinct()
            p = Paginator(get_date, 30)
            page_number = request.GET.get('page')
            if page_number == None:
                page_number=1
            try:
                page_obj = p.get_page(page_number)
            except PageNotAnInteger:
                page_obj = p.page(1)
            except EmptyPage:
                page_obj = p.page(p.num_pages)
             
            for dates in page_obj:
                total_order, item_count, total_paid, total_unpaid, discounts, shipping= Order.sells_over_time_all_data(dates[0])
                if total_order['total_price'] is None:
                    total_order['total_price']=0
                if discounts['total_price'] is None:
                    discounts['total_price'] = 0
                if total_paid['total_price'] is None:
                    total_paid['total_price']=0
                if total_unpaid['total_price'] is None:
                    total_unpaid['total_price']=0
                if shipping['total_price'] is None:
                    shipping['total_price']=0
                
                net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])

                new_list.append({
                    'status':dates[0],
                    'total':total_order['total_price'],
                    'item_count':item_count,
                    'paid':total_paid['total_price'],
                    'unpaid':total_unpaid['total_price'],
                    'discount':discounts['total_price'],
                    'shipping': shipping['total_price'],
                    'net_sells':net_sells
                })
            return render(request, self.template_name, {'new_list':new_list, 'order_status':order_status, 'time_range':time_range, 'page_obj':page_obj, 'page_number':int(page_number)})




class ExportCsvViewSalesOverTime(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name="admin_view/sales/sales_order_report/sales_over_time.html"
    permission_required = ['sales.view_order']

    def get(self, request, *arge, **kwargs):
        new_list = []
        get_date = Order.objects.order_by("-placed_on").values_list('placed_on').distinct()
        for dates in get_date:
            total_order, item_count, total_paid, total_unpaid, discounts, shipping= Order.sells_over_time_all_data(dates[0])
            if total_order['total_price'] is None:
                total_order['total_price']=0
            if discounts['total_price'] is None:
                discounts['total_price'] = 0
            if total_paid['total_price'] is None:
                total_paid['total_price']=0
            if total_unpaid['total_price'] is None:
                total_unpaid['total_price']=0
            if shipping['total_price'] is None:
                shipping['total_price']=0
            
            net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price'])

            new_list.append({
                'status':dates[0],
                'total':total_order['total_price'],
                'item_count':item_count,
                'paid':total_paid['total_price'],
                'unpaid':total_unpaid['total_price'],
                'discount':discounts['total_price'],
                'shipping': shipping['total_price'],
                'net_sells':net_sells
            })
        title = (new_list[0].keys())
        response = export_csv_file_sells_over_time(new_list, title)
        return response

    def post(self, request, *args, **kwargs):
        date__range=self.request.POST.get('date_range',None)
        order_status = self.request.POST.get('order_status',None)
        time_range = self.request.POST.get('time_range', None)
        
        context = {
            'date_range': date__range,
            'order_status':order_status,
            'time_range':time_range,
            
        }
        new_list=[]
        if date__range or order_status or time_range: #or year or month:
            if order_status is not None and time_range:
                if order_status=='month' and time_range == 'daily':
                    current_month = date.today().month
                    current_year= date.today().year
                    from calendar import monthrange
                    num_days = monthrange(current_year, current_month)[1]
                    
                    total_sells = 0
                    for i in range(1, num_days+1):
                        get_date = datetime.strptime(f'{current_year}-{current_month}-{i}', '%Y-%m-%d').date()
                        data = sells_over_time_filter_date_range(get_date)
                        total_sells += data['total']
                        data.update({'status':get_date})
                        new_list.append(data)
                    
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                

                elif order_status == 'year' and time_range == 'daily':
                    # import datetime
                    current_year= date.today().year
                    start_date = datetime.strptime(f'{current_year}-{1}-{1}', '%Y-%m-%d').date()
                    end_date= datetime.strptime(f'{current_year}-{12}-{30}', '%Y-%m-%d').date()
                    date_list = date_range(start_date, end_date)
                
                    total_sells = 0
                    for _date_ in date_list:
                        data = sells_over_time_filter_date_range(_date_)
                        total_sells += data['total']
                        data.update({'status':_date_})
                        new_list.append(data)

                    
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context,'date_range':date__range, 'order_status':order_status, 'time_range':time_range, 'page_obj':page_obj, 'page_number':int(page_number)})
                    
                elif order_status=='month' and time_range=='weekly':
                    year= date.today().year
                    month = date.today().month
                    week = week_from_date(date(year, month, 1))
                    only_week_ = list(week)[1]
                    week_list_of_month = [only_week_, only_week_+1,only_week_+2,only_week_+3,only_week_+4]
                    i=1
                    for weeks in week_list_of_month:
                        data = sells_over_time_week_month_and_yearly_basis(weeks, month, year)
                        status = (f'{year}/{month}/Week-{i}')
                        data.update({'status':status})
                        new_list.append(data)
                        i+=1
                    
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                    
                elif order_status == 'week' and time_range == 'daily':
                    date_ = timezone.now().isocalendar()[1]
                    year= date.today().year
                    day_list = weeknum_to_dates(date_, year)
                    total_sells = 0
                    for day in day_list:
                        data = sells_over_time_filter_date_range(day)
                        total_sells += data['total']
                        data.update({'status':day})
                        new_list.append(data)
                    
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    

                elif order_status == 'year' and time_range=='weekly':
                    year= date.today().year
                    month = date.today().month
                    for j in range(1,52):
                        data = sells_over_time_week_month_and_yearly_basis(j, month, year)
                        status = (f'{year}-Week-{j}')
                        data.update({'status':status})
                        new_list.append(data)
                    
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                    
                elif order_status == 'year' and time_range == 'monthly':
                    month_list = [1,2,3,4,5,6,7,8,9,10,11,12]
                    current_year= date.today().year

                    for months in month_list:
                        data_retrive = sells_over_time_month_and_yearly_basis(months, current_year)
                        status = datetime.strptime(f'{current_year}-{months}', '%Y-%m').date()
                        data_retrive.update({'status':status})
                        new_list.append(data_retrive)
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                    
            if order_status and not date__range and not time_range:
                if order_status == 'today':
                    date_ = timezone.now()
                    new_list= Order.sells_over_time(date_)
                    new_list[0].update({'status':order_status})
                
                elif order_status.strip(' ') == 'yesterday':
                    date_ = (timezone.now() - timedelta(1)).strftime('%Y-%m-%d')
                    new_list = Order.sells_over_time(date_)
                    new_list[0].update({'status':order_status})
                    
                elif order_status == 'week':
                    date_ = timezone.now().isocalendar()[1]
                    new_list = Order.sells_over_time_week(date_)
                    new_list[0].update({'status':'This Week'})

                elif order_status == 'month':
                    date_ = timezone.now().month
                    new_list = Order.sells_over_time_month(date_)
                    new_list[0].update({'status':'This Month'})

                elif order_status == 'year':
                    date_ = timezone.now().year
                    new_list = Order.sells_over_time_year(date_)
                    new_list[0].update({'status':f'In {date_}'})
                # return render(request, self.template_name, {'new_list':new_list, 'context':context})
               
            

            if  date__range and time_range:
                if len(date__range)>1:
                    date__range=date__range.split('to')
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    if time_range == 'daily':
                        date_list = date_range(start_date, end_date)
                        
                        total_sells = 0
                        for _date_ in date_list:
                            data = sells_over_time_filter_date_range(_date_)
                            total_sells += data['total']
                            data.update({'status':_date_})
                            new_list.append(data)
                        # return render(request, self.template_name, {'new_list':new_list, 'context':context, 'order_status':order_status, 'date_range':date_range_req, 'time_range':time_range, 'page_obj':page_obj, 'page_number':int(page_number)})
                    

                    elif time_range == 'weekly':
                        week_list = find_weeks(start_date, end_date)
                        total_sells = 0
                        i=1
                        for week in week_list:
                            data = sells_over_time_filter_week(week[-2:])
                            total_sells += data['total']
                            data.update({'status':f'Week-{i}'})
                            new_list.append(data)
                            i+=1
                    
                    elif time_range == 'monthly':
                        months = months_between(start_date, end_date)
                        total_sells = 0
                        for month in months:
                            data = sells_over_time_monthly(month)
                            total_sells += data['total']
                            data.update({'status':f'Month-{month}'})
                            new_list.append(data)

                    elif time_range == 'yearly':
                        start_year = start_date.year
                        end_year = end_date.year
                        diff = end_year-start_year
                        year_list = []
                        if diff !=0:
                            num_year = diff
                            for i in range(num_year+1):
                                years = start_year+i
                                year_list.append(years)
                            total_sells=0
                            for year in year_list:
                                data = sells_over_time_yearly_basis(year)
                                total_sells += data['total']
                                data.update({'status':f'In Year {year}'})
                                new_list.append(data)

                        else:
                            data = sells_over_time_yearly_basis(start_year)
                            total_sells = data['total']
                            data.update({'status':f'In Year {start_year}'})
                            new_list.append(data)
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                    
                else:
                    start = date__range[0].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_range_on_date(start_date)
                    # return render(request, self.template_name, {'new_list':new_list, 'context':context})
                
                

            if date__range:
                date__range=date__range.split('to')
                if len(date__range)>1:
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_date_range(start_date, end_date)
                    
                else:
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    new_list = Order.sells_over_time_range_on_date(start_date) 

                # return render(request, self.template_name, {'new_list':new_list, 'context':context})
        title = (new_list[0].keys())
        response = export_csv_file_sells_over_time(new_list, title)
        return response


class SalseByProductView(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name = "admin_view/sales/sales_order_report/sales_by_product.html"
    permission_required = ['sales.change_order']
    paginate_by=50

    def get(self, request, *args, **kwargs):
        date_req = self.request.GET.get('date_range',None)
        date__range=self.request.GET.get('date_range',None)
        order_status = self.request.GET.get('order_status',None)

        context = {
            'date_range':date__range,
            'order_status': order_status
        }
        if date__range or order_status:
            if order_status is not None :
                if order_status == 'today':
                    try:
                        today_date = timezone.now()
                        total_product = OrderItem.objects.order_by().values_list('product').distinct()
                        product_count_list = []
                        for product_id in total_product:
                            product_obj = OrderItem.objects.filter(product=product_id, order__placed_on=today_date)
                            product_name = product_obj.values('product__varient_name')
                            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                            total = product_obj.values('total').aggregate(Sum('total'))
                            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                            product_count_list.append({
                                'product_name':product_name[0]['product__varient_name'],
                                'item_count': len(product_name),
                                'sub_total': sub_total['sub_total__sum'],
                                'total': total['total__sum'],
                                'quantity':quantity['quantity__sum'],
                                'discount':total['total__sum']-sub_total['sub_total__sum']
                                })  
                        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                        return render(request, self.template_name, {'product_count':best_selling_today_list, 'context':context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})
                        
                if order_status.strip(' ') == 'yesterday':
                    try:
                        yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
                        total_product = OrderItem.objects.order_by().values_list('product').distinct()

                        product_count_list = []
                        for product_id in total_product:
                            product_obj = OrderItem.objects.filter(product=product_id, order__placed_on=yesterday)
                            product_name = product_obj.values('product__varient_name')
                            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                            total = product_obj.values('total').aggregate(Sum('total'))
                            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                            product_count_list.append({
                                'product_name':product_name[0]['product__varient_name'],
                                'item_count': len(product_name),
                                'sub_total': sub_total['sub_total__sum'],
                                'total': total['total__sum'],
                                'quantity':quantity['quantity__sum'],
                                'discount':total['total__sum']-sub_total['sub_total__sum']
                                })  
                    
                        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                        return render(request, self.template_name, {'product_count':best_selling_today_list, 'context': context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})


                if order_status == 'week':
                    try:
                        weeks = timezone.now().isocalendar()[1]
                        total_product = OrderItem.objects.order_by().values_list('product').distinct()
                        
                        product_count_list = []
                        for product_id in total_product:
                            product_obj = OrderItem.objects.filter(product=product_id, order__placed_on__week=weeks)
                            product_name = product_obj.values('product__varient_name')
                            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                            total = product_obj.values('total').aggregate(Sum('total'))
                            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                            product_count_list.append({
                                'product_name':product_name[0]['product__varient_name'],
                                'item_count': len(product_name),
                                'sub_total': sub_total['sub_total__sum'],
                                'total': total['total__sum'],
                                'quantity':quantity['quantity__sum'],
                                'discount':total['total__sum']-sub_total['sub_total__sum']
                                })  
                
                        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                        return render(request, self.template_name, {'product_count':best_selling_today_list, 'context':context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})

                    

                if order_status == 'month':
                    try:
                        months = timezone.now().month
                        total_product = OrderItem.objects.order_by().values_list('product').distinct()
                        product_count_list = []
                        for product_id in total_product:
                            product_obj = OrderItem.objects.filter(product=product_id, order__placed_on__month=months)
                            product_name = product_obj.values('product__varient_name')
                            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                            total = product_obj.values('total').aggregate(Sum('total'))
                            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                            product_count_list.append({
                                'product_name':product_name[0]['product__varient_name'],
                                'item_count': len(product_name),
                                'sub_total': sub_total['sub_total__sum'],
                                'total': total['total__sum'],
                                'quantity':quantity['quantity__sum'],
                                'discount':total['total__sum']-sub_total['sub_total__sum']
                                }) 

                
                        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                        return render(request, self.template_name, {'product_count':best_selling_today_list, 'context':context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})

                if order_status == 'year':
                    try:
                        years = timezone.now().year
                        total_product = OrderItem.objects.order_by().values_list('product').distinct()
                        product_count_list = []
                        for product_id in total_product:
                            product_obj = OrderItem.objects.filter(product=product_id, order__placed_on__year=years)
                            product_name = product_obj.values('product__varient_name')
                            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                            total = product_obj.values('total').aggregate(Sum('total'))
                            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                            product_count_list.append({
                                'product_name':product_name[0]['product__varient_name'],
                                'item_count': len(product_name),
                                'sub_total': sub_total['sub_total__sum'],
                                'total': total['total__sum'],
                                'quantity':quantity['quantity__sum'],
                                'discount':total['total__sum']-sub_total['sub_total__sum']
                                }) 
                 
                        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                        return render(request, self.template_name, {'product_count':best_selling_today_list, 'context':context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})

        
                if date__range and len(date__range)<1:
                    return redirect(self.request.META['HTTP_REFERER'])
                
                if date__range:
                    try:
                        date__range=date__range.split('to')
                        if len(date__range)>1:
                            start = date__range[0].strip()
                            end=date__range[1].strip()
                            start_date = datetime.strptime(start, '%Y-%m-%d').date()
                            end_date = datetime.strptime(end, '%Y-%m-%d').date()

                            total_product = OrderItem.objects.order_by().values_list('product').distinct()
                            product_count_list = []
                            for product_id in total_product:
                                product_obj = OrderItem.objects.filter(product=product_id, order__placed_on__range=[start_date, end_date])
                                product_name = product_obj.values('product__varient_name')
                                sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                                total = product_obj.values('total').aggregate(Sum('total'))
                                quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                                product_count_list.append({
                                    'product_name':product_name[0]['product__varient_name'],
                                    'item_count': len(product_name),
                                    'sub_total': sub_total['sub_total__sum'],
                                    'total': total['total__sum'],
                                    'quantity':quantity['quantity__sum'],
                                    'discount':total['total__sum']-sub_total['sub_total__sum']
                                    }) 
                        
                            best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                            return render(request, self.template_name, {'product_count':best_selling_today_list, 'date_range_req':date__range, 'context':context})
                    except:
                        message="Result Not Found."
                        return render(request, self.template_name, {'message':message})


                    else:
                        try:
                            start = date__range[0]
                            start_date = datetime.strptime(start, '%Y-%m-%d').date()

                            total_product = OrderItem.objects.order_by().values_list('product').distinct()
                            product_count_list = []
                            for product_id in total_product:
                                product_obj = OrderItem.objects.filter(product=product_id, order__placed_on=start_date)
                                product_name = product_obj.values('product__varient_name')
                                sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                                total = product_obj.values('total').aggregate(Sum('total'))
                                quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                                product_count_list.append({
                                    'product_name':product_name[0]['product__varient_name'],
                                    'item_count': len(product_name),
                                    'sub_total': sub_total['sub_total__sum'],
                                    'total': total['total__sum'],
                                    'quantity':quantity['quantity__sum'],
                                    'discount':total['total__sum']-sub_total['sub_total__sum']
                                    }) 
                            best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
                            return render(request, self.template_name, {'product_count':best_selling_today_list, 'date_range_req':start_date, 'context':context})
                        except:
                            message="Result Not Found."
                            return render(request, self.template_name, {'message':message})
                            
        else:
            total_product = OrderItem.objects.values_list('product').distinct()
            p = Paginator(total_product, 30)
            page_number = request.GET.get('page')
            if page_number == None:
                page_number=1
            try:
                page_obj = p.get_page(page_number)
            except PageNotAnInteger:
                page_obj = p.page(1)
            except EmptyPage:
                page_obj = p.page(p.num_pages)
            product_count_list = []
            for product_id in page_obj:
                product_obj = OrderItem.objects.filter(product=product_id)
                product_name = product_obj.values('product__varient_name')
                sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
                total = product_obj.values('total').aggregate(Sum('total'))
                quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

                product_count_list.append({
                    'product_name':product_name[0]['product__varient_name'],
                    'item_count': len(product_name),
                    'sub_total': sub_total['sub_total__sum'],
                    'total': total['total__sum'],
                    'quantity':quantity['quantity__sum'],
                    'discount':total['total__sum']-sub_total['sub_total__sum']
                })    

            product_count_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
            return render(request, self.template_name, {'product_count': product_count_list, 'page_obj':page_obj, 'page_number': int(page_number)})



class ExportSalesByProductView(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    template_name = "admin_view/sales/sales_order_report/sales_by_product.html"
    permission_required = ['sales.change_order']

    def post(self,request,*args,**kwargs): 
        # date_req = self.request.POST.get('date_range',None)
        date__range=self.request.POST.get('date_range',None)
        order_status = self.request.POST.get('order_status',None)

        # try:
        if order_status is not None:
            if order_status == 'today':
                today_date = timezone.now()
                best_selling_product_today_list = product_selling_today(today_date)
                best_selling_today_list = []
                for item in best_selling_product_today_list:
                    product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                    for products in product_obj:
                        best_selling_today_list.append({
                            'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                            'product_name': products['product_name'],
                            'item_count': '-',
                            'sub_total': products['sub_total'],
                            'total': products['total'],
                            'quantity':products['quantity'],
                            'discount':(products['total']-products['sub_total']),
                        })
                best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                header = best_selling_today_list[0].keys()
                response = export_csv_file_sells_over_time(best_selling_today_list, header)
                return response
                                        
            if order_status.strip(' ') == 'yesterday':
                yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
                best_selling_product_today_list = product_selling_today(yesterday)
                best_selling_today_list = []
                for item in best_selling_product_today_list:
                    product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                    for products in product_obj:
                        best_selling_today_list.append({
                            'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                            'item_count': '-',
                            'sub_total': products['sub_total'],
                            'total': products['total'],
                            'quantity':products['quantity'],
                            'discount':(products['total']-products['sub_total']),
                        })
                best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                header = best_selling_today_list[0].keys()
                response = export_csv_file_sells_over_time(best_selling_today_list, header)
                return response

            if order_status == 'week':
                weeks = timezone.now().isocalendar()[1]
                best_selling_product_today_list = product_sells_week(weeks)
                best_selling_today_list = []
                for item in best_selling_product_today_list:
                    product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                    for products in product_obj:
                        best_selling_today_list.append({
                            'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                            'item_count': '-',
                            'sub_total': products['sub_total'],
                            'total': products['total'],
                            'quantity':products['quantity'],
                            'discount':(products['total']-products['sub_total']),
                        })
                best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                header = best_selling_today_list[0].keys()
                response = export_csv_file_sells_over_time(best_selling_today_list, header)
                return response
                

            if order_status == 'month':
                months = timezone.now().month
                best_selling_product_today_list = product_sells_month(months)
                best_selling_today_list = []
                for item in best_selling_product_today_list:
                    product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                    for products in product_obj:
                        best_selling_today_list.append({
                            'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                            'item_count': '-',
                            'sub_total': products['sub_total'],
                            'total': products['total'],
                            'quantity':products['quantity'],
                            'discount':(products['total']-products['sub_total']),
                        })
                best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                header = best_selling_today_list[0].keys()
                response = export_csv_file_sells_over_time(best_selling_today_list, header)
                return response

            if order_status == 'year':
                years = timezone.now().year
                best_selling_product_today_list = product_sells_years(years)
                best_selling_today_list = []
                for item in best_selling_product_today_list:
                    product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                    for products in product_obj:
                        best_selling_today_list.append({
                            'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                            'item_count': '-',
                            'sub_total': products['sub_total'],
                            'total': products['total'],
                            'quantity':products['quantity'],
                            'discount':(products['total']-products['sub_total']),
                        })
                best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                header = best_selling_today_list[0].keys()
                response = export_csv_file_sells_over_time(best_selling_today_list, header)
                return response

    
            if date__range and len(date__range)<1:
                return redirect(self.request.META['HTTP_REFERER'])
            
            if date__range:
                date__range=date__range.split('to')
                if len(date__range)>1:
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    best_selling_product_today_list = product_sells_in_date_range(start_date, end_date)
                    date_range = f'{start_date} To {end_date}'
                    best_selling_today_list = []
                    for item in best_selling_product_today_list:
                        product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                        for products in product_obj:
                            best_selling_today_list.append({
                                'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                                'item_count': '-',
                                'sub_total': products['sub_total'],
                                'total': products['total'],
                                'quantity':products['quantity'],
                                'discount':(products['total']-products['sub_total']),
                            })
                    best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                    header = best_selling_today_list[0].keys()
                    response = export_csv_file_sells_over_time(best_selling_today_list,header)
                    return response

                else:
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    best_selling_today_list = []
                    best_selling_product_today_list = product_sells_in_date(start_date)
                    for item in best_selling_product_today_list:
                        product_obj =  OrderItem.objects.filter(order__order_number=item).values()
                        for products in product_obj:
                            best_selling_today_list.append({
                                'product_name': ProductVarient.objects.filter(id=products['product_id']).values('varient_name')[0]['varient_name'],
                                'item_count': '-',
                                'sub_total': products['sub_total'],
                                'total': products['total'],
                                'quantity':products['quantity'],
                                'discount':(products['total']-products['sub_total']),
                            })
                    best_selling_today_list = sorted(best_selling_today_list, key = lambda i: i['quantity'],reverse=True)
                    header = best_selling_today_list[0].keys()

                    response = export_csv_file_sells_over_time(best_selling_today_list, header)
                    return response
    
    def get(self, request):
        total_product = OrderItem.objects.order_by().values_list('product').distinct()
        product_count_list = []
        for product_id in total_product:
            product_obj = OrderItem.objects.filter(product=product_id)
            product_name = product_obj.values('product__varient_name')
            sub_total = product_obj.values('sub_total').aggregate(Sum('sub_total'))
            total = product_obj.values('total').aggregate(Sum('total'))
            quantity = product_obj.values('quantity').aggregate(Sum('quantity'))

            product_count_list.append({
                'product_name':product_name[0]['product__varient_name'],
                'item_count': len(product_name),
                'sub_total': sub_total['sub_total__sum'],
                'total': total['total__sum'],
                'quantity':quantity['quantity__sum'],
                'discount':total['total__sum']-sub_total['sub_total__sum']
            })
        best_selling_today_list = sorted(product_count_list, key = lambda i: i['quantity'],reverse=True)
        header = best_selling_today_list[0].keys()
        response = export_csv_file_sells_over_time(best_selling_today_list, header)
        return response




class SalesByCostumer(PermissionRequiredMixin, SuperUserCheck, TemplateView):
    template_name = "admin_view/sales/sales_order_report/sales_by_costumer.html"
    permission_required = ['sales.change_order']

    def get(self, request, *args, **kwargs):   
        old_qs = Order.objects.order_by('-id')
        # new_costumer = old_qs.values('delivery_address__contact_number').order_by().filter(id__count__gt=0)
        

        order_keyword = self.request.GET.get('order_keyword',None)
        # date_req = self.request.GET.get('date_range',None)
        date__range=self.request.GET.get('date_range',None)
        date_range=date__range
        context ={
            'order_keyword':order_keyword,
            'date_range': date__range
        }
        if order_keyword is not None or date__range:
            if date__range and len(date__range)<1:
                return redirect(self.request.META['HTTP_REFERER'])
        
            if order_keyword:
                qs=old_qs.filter(Q(delivery_address__receiver_fullname__icontains=order_keyword) | Q(delivery_address__contact_number__icontains=order_keyword))

            if date__range:
                date__range=date__range.split('to')
                if len(date__range)>1:
                    start = date__range[0].strip()
                    end=date__range[1].strip()
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    end_date = datetime.strptime(end, '%Y-%m-%d').date()
                    qs=old_qs.filter(Q(placed_on__range=[start_date,end_date])) 
                else:
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    qs=old_qs.filter(Q(placed_on=start_date))

            
                # p = Paginator(qs, 2)
                # try:
                #     page_obj1 = p.get_page(page_number)
                # except PageNotAnInteger:
                #     page_obj1 = p.page(1)
                # except EmptyPage:
                #     page_obj1 = p.page(p.num_pages)
            return super(SalesByCostumer,self).get(request,qs = qs, order_keyword=order_keyword, context=context)
            
        else:
            mobile_number = Order.objects.order_by('-delivery_address__contact_number').values('delivery_address__contact_number').distinct()
            costumer_detail_list = []
            p = Paginator(mobile_number, 50)
            page_number = request.GET.get('page')
            if page_number is None:
                page_number=1
            try:
                page_obj = p.get_page(page_number)
            except PageNotAnInteger:
                page_obj = p.page(1)
            except EmptyPage:
                page_obj = p.page(p.num_pages)
            for item in page_obj:
                total_orders = Order.objects.filter(delivery_address__contact_number =item['delivery_address__contact_number']).count()
                total_paid = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number'], payment_status='Paid').aggregate(total_price=Sum('total'))['total_price']
                total_unpaid = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number'], payment_status='Awaiting Payment').aggregate(total_price=Sum('total'))['total_price']
                discount = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).aggregate(discount=Sum('discount'))['discount']
                shipping_cost = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).aggregate(shipping_cost=Sum('shipping_cost'))['shipping_cost']
                quantity = OrderItem.objects.filter(order__delivery_address__contact_number=item['delivery_address__contact_number']).aggregate(quantity=Sum('quantity'))['quantity']
                placed_on = Order.objects.filter(delivery_address__contact_number=item['delivery_address__contact_number']).values('placed_on').latest('placed_on')

                if total_paid:
                    total_paid=total_paid
                else:
                    total_paid=0
                if total_unpaid:
                    total_unpaid=total_unpaid
                else:
                    total_unpaid=0
                if discount:
                    discount=discount
                else:
                    discount=0
                if shipping_cost:
                    shipping_cost=shipping_cost
                else:
                    shipping_cost=0
                if total_paid or total_unpaid !=0:
                    total_sales_value = (total_paid+total_unpaid+shipping_cost)-discount
                else:
                    total_sales_value=0
                name_list = DeliveryAddress.objects.values('sender_fullname').filter(contact_number=item['delivery_address__contact_number'])
                costumer_detail_list.append({
                    'name': name_list[0]['sender_fullname'],
                    'mobile': item['delivery_address__contact_number'],
                    'orders': total_orders,
                    'total_paid': total_paid,
                    'total_unpaid': total_unpaid,
                    'discount':discount,
                    'shipping_cost':shipping_cost,
                    'total_value':total_sales_value,
                    'quantity':quantity,
                    'placed_on':placed_on
                })
            return super(SalesByCostumer,self).get(request,costumer_detail = costumer_detail_list,page_obj = page_obj, context=context, page_number=int(page_number))



class SalesByCostumerExportCSView(PermissionRequiredMixin, SuperUserCheck, TemplateView):
    template_name = "admin_view/sales/sales_order_report/sales_by_costumer.html"
    permission_required = ['sales.change_order']

    def get(self, *args, **kwargs):
        old_qs = Order.objects.order_by('-id')
        data_list = []
        for item in old_qs:
            costumer_name, contact_number, placed_on, quantity, item_count, gross_sells, shipping_cost, discounts, status, net_sells = Order.sales_by_costumer_all_data(item)
            data_list.append({
                'order_number':item,
                'costumer_name': costumer_name[0]['delivery_address__receiver_fullname'],
                'contact_number':contact_number[0]['delivery_address__contact_number'],
                'order_date':placed_on[0]['placed_on'],
                'quantity':quantity,
                'item_count':item_count,
                'gross_sells':gross_sells,
                'shipping_cost':shipping_cost,
                'discountts':discounts,
                'payment_status': status,
                'net_sells':net_sells
            })
        header = data_list[0].keys()
        response = export_csv_file_sells_over_time(data_list, header)
        return response


class OrderReport(PermissionRequiredMixin, SuperUserCheck, TemplateView):
    template_name = "admin_view/sales/sales_order_report/order_report.html"
    permission_required = ['sales.change_order']

    def get(self, request, *args, **kwargs):
        time_range = self.request.GET.get('time_range', None)
        date__range=self.request.GET.get('date_range',None)
        status = self.request.GET.get('order_status')
        month = date.today().month
        year= date.today().year
        today = timezone.now()
        week = timezone.now().isocalendar()[1]

        context = {
            'time_range':time_range,
            'date_range': date__range,
            'order_status': status,
        }
        if time_range or date__range or status:
            if status:
                if status=='today':
                    qs = Order.objects.filter(placed_on=today).values()
                  
                if status == 'yesterday':
                    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
                    qs = Order.objects.filter(placed_on=yesterday)
                    
                if status == 'week':
                    qs = Order.objects.filter(placed_on__week=week).values()
                   
                if status == 'month':
                    qs = Order.objects.filter(placed_on__month=month).values()
                    
                if status == 'year':
                    qs = Order.objects.filter(placed_on__year=year).values()


            if status == 'week' and time_range == 'daily':
                day_list = weeknum_to_dates(week, year)
                start_date = day_list[-1]
                end_date=  day_list[0]
                qs = Order.objects.filter(placed_on__range=[start_date,end_date]).values()

            elif status == 'month' and time_range == 'daily':
                from calendar import monthrange
                num_days = monthrange(year, month)[1]
                start_date = datetime.strptime(f'{year}-{month}-{1}', '%Y-%m-%d').date()
                end_date = datetime.strptime(f'{year}-{month}-{num_days}', '%Y-%m-%d').date()
                qs = Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                
            elif status == 'month' and time_range == 'weekly':
                week = week_from_date(date(year, month, 1))
                only_week_ = list(week)[1]
                week_list_of_month = [only_week_, only_week_+1,only_week_+2,only_week_+3,only_week_+4]
                for weeks in week_list_of_month:
                    qs = Order.objects.filter(placed_on__week=weeks).values()
                    
            elif status == 'year' and time_range == 'daily' or status=='year' and time_range=='monthly' or status=='year' and time_range=='weekly':
                start_date = datetime.strptime(f'{year}-{1}-{1}', '%Y-%m-%d').date()
                end_date= datetime.strptime(f'{year}-{12}-{30}', '%Y-%m-%d').date()
                qs = Order.objects.filter(placed_on__range=[start_date, end_date]).values()

           
            if date__range:
                if date__range and len(date__range)<1:
                    return redirect(self.request.META['HTTP_REFERER'])

                date__range=date__range.split('to')
                if len(date__range)>1:
                    if date__range and time_range == 'daily' or time_range=='weekly' or time_range=='monthly' or time_range == 'yearly':
                        start = date__range[0].strip()
                        end=date__range[1].strip()
                        start_date = datetime.strptime(start, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end, '%Y-%m-%d').date()
                        qs=Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                    else:
                        start = date__range[0].strip()
                        end=date__range[1].strip()
                        start_date = datetime.strptime(start, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end, '%Y-%m-%d').date()
                        qs=Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                        
                else:   
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    qs=Order.objects.filter(placed_on=start_date).values()
                    
        else:
            qs = Order.objects.order_by('-id')
        p = Paginator(qs, 50)
        page_number = request.GET.get('page')
        if page_number == None:
            page_number=1
        try:
            page_obj = p.get_page(page_number)
        except PageNotAnInteger:
            page_obj = p.page(1)
        except EmptyPage:
            page_obj = p.page(p.num_pages)
        return super(OrderReport,self).get(request,page_obj = page_obj, page_number=int(page_number), context=context, time_range=time_range, date_range=date__range, order_status=status)



class ExportOrderReportToCsv(PermissionRequiredMixin, SuperUserCheck, TemplateView):
    template_name = "admin_view/sales/sales_order_report/order_report.html"
    permission_required = ['sales.view_order']
    
    def post(self, request, *args, **kwargs):

        time_range = self.request.POST.get('time_range', None)
        year = self.request.POST.get('year', None)
        month = self.request.POST.get('month', None)
        date__range=self.request.POST.get('date_range',None)
        status = self.request.POST.get('status', None)

        month = date.today().month
        year= date.today().year
        today = timezone.now()
        week = timezone.now().isocalendar()[1]

        if date__range and len(date__range)<1:
            return redirect(self.request.META['HTTP_REFERER'])

        qs_list = []
        if time_range or date__range or status:
            if status:
                if status=='today':
                    qs = Order.objects.filter(placed_on=today).values()
                  
                if status == 'yesterday':
                    yesterday = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')
                    qs = Order.objects.filter(placed_on=yesterday)
                    
                if status == 'week':
                    qs = Order.objects.filter(placed_on__week=week).values()
                   
                if status == 'month':
                    qs = Order.objects.filter(placed_on__month=month).values()
                    
                if status == 'year':
                    qs = Order.objects.filter(placed_on__year=year).values()


            if status == 'week' and time_range == 'daily':
                day_list = weeknum_to_dates(week, year)
                start_date = day_list[-1]
                end_date=  day_list[0]
                qs = Order.objects.filter(placed_on__range=[start_date,end_date]).values()

            elif status == 'month' and time_range == 'daily':
                from calendar import monthrange
                num_days = monthrange(year, month)[1]
                start_date = datetime.strptime(f'{year}-{month}-{1}', '%Y-%m-%d').date()
                end_date = datetime.strptime(f'{year}-{month}-{num_days}', '%Y-%m-%d').date()
                qs = Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                
            elif status == 'month' and time_range == 'weekly':
                week = week_from_date(date(year, month, 1))
                only_week_ = list(week)[1]
                week_list_of_month = [only_week_, only_week_+1,only_week_+2,only_week_+3,only_week_+4]
                for weeks in week_list_of_month:
                    qs = Order.objects.filter(placed_on__week=weeks).values()
                    
            elif status == 'year' and time_range == 'daily' or status=='year' and time_range=='monthly' or status=='year' and time_range=='weekly':
                start_date = datetime.strptime(f'{year}-{1}-{1}', '%Y-%m-%d').date()
                end_date= datetime.strptime(f'{year}-{12}-{30}', '%Y-%m-%d').date()
                qs = Order.objects.filter(placed_on__range=[start_date, end_date]).values()

           
            if date__range:
                if date__range and len(date__range)<1:
                    return redirect(self.request.META['HTTP_REFERER'])

                date__range=date__range.split('to')
                if len(date__range)>1:
                    if date__range and time_range == 'daily' or time_range=='weekly' or time_range=='monthly' or time_range == 'yearly':
                        start = date__range[0].strip()
                        end=date__range[1].strip()
                        start_date = datetime.strptime(start, '%Y-%m-%d').date()
                        end_date =datetime.strptime(end, '%Y-%m-%d').date()
                        qs=Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                    else:
                        start = date__range[0].strip()
                        end=date__range[1].strip()
                        start_date = datetime.strptime(start, '%Y-%m-%d').date()
                        end_date = datetime.strptime(end, '%Y-%m-%d').date()
                        qs=Order.objects.filter(placed_on__range=[start_date,end_date]).values()
                        
                else:   
                    start = date__range[0]
                    start_date = datetime.strptime(start, '%Y-%m-%d').date()
                    qs=Order.objects.filter(placed_on=start_date).values()
        try: 
            for item in qs:
                data_dis = {
                    "order_number": item['order_number'],
                    "placed_on": item['placed_on'],
                    "total":item['total'],
                    "sub_total":item['sub_total_order'],
                    "discount": item['discount'],
                    "shipping": item['shipping_cost'],
                    "order_status": item['order_status'],
                    "payment_status": item['payment_status'],
                    "net_sells":item['total'],
                }
                qs_list.append(data_dis)
            title = qs_list[0].keys()
            response = export_csv_file_sells_over_time(qs_list, title)
            return response
        except:
            messages.error(request, 'Data Not Found!!')
            return redirect('sales:order-report')
        

    def get(self, request):
        qs_list=[]
        qs = Order.objects.values('order_number', 'placed_on', 'total', 'sub_total_order', 'discount', 'shipping_cost', 'order_status', 'payment_status')
        for item in qs:
            data_dis = {
                "order_number": item['order_number'],
                "placed_on": item['placed_on'],
                "total":item['total'],
                "sub_total":item['sub_total_order'],
                "discount": item['discount'],
                "shipping": item['shipping_cost'],
                "order_status": item['order_status'],
                "payment_status": item['payment_status'],
                "net_sells":item['total'],
            }
            qs_list.append(data_dis)

        title = qs_list[0].keys()
        response = export_csv_file_sells_over_time(qs_list, title)
        return response

@permission_required('sales.view_vendor',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def vendorList(request):
    """vandor listing"""
    if request.method=='GET':
        vendor=Vendor.objects.order_by('-id')
        form=VendorForm()
        keywords=request.GET.get('keywords',None)

        if keywords:
            vendor=Vendor.objects.filter(Q(name__icontains=keywords))
        return render(request,'admin_view/sales/vendor.html',{'vendor':vendor,'keywords':keywords,'form':form})

@permission_required('sales.add_vendor',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def vendorAjaxCreate(request):
    """creating vendor"""
    if request.method == 'POST':
        form = VendorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                            request, "Vendor has been Added Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})



@permission_required('sales.change_vendor',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def vendorAjaxUpdate(request,pk):
    """Updating vendor"""
    if request.method=='GET':
        vendor=get_object_or_404(Vendor,id=pk)
        return JsonResponse({'status':'success','addons':model_to_dict(vendor)})

    if request.method == 'POST':
        vendor= get_object_or_404(Vendor,id=pk)
        form=VendorForm(request.POST,instance=vendor)
        if form.is_valid():
            form.save()
            messages.success(
                            request, "Vendor has been Added Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})

@permission_required('sales.delete_vendor',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteVendorBulk(request):
    """deleting vendor in bulk"""
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            try:
                vendor=Vendor.objects.filter(id=item_id[int(i)]).delete()
                messages.success(request, "Selected vendor has been removed successfully.")
            except ProtectedError as e:
                messages.error(request,'Cannot delete some vendor because they have orders.')
    return redirect(request.META['HTTP_REFERER'])

@permission_required('sales.delete_vendor',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def vendorDelete(request,pk):
    """Deleting particular vendor"""
    if request.method=='POST':
        try:
            vendor=get_object_or_404(Vendor,id=pk).delete()
            messages.success(request, "Vendor has been removed successfully.")
        except ProtectedError as e:
            messages.error(request, "Cant delete this vendor because this vendor has orders.")
        return redirect('sales:vendor-list')




@permission_required('sales.view_factory',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def factoryList(request):
    """vandor listing"""
    if request.method=='GET':
        factory=Factories.objects.order_by('-id')
        form=FactoryModelForm()
        keywords=request.GET.get('keywords',None)

        if keywords:
            factory=Factories.objects.filter(Q(name__icontains=keywords))
        return render(request,'admin_view/sales/factory.html',{'factory':factory,'keywords':keywords,'form':form})

@permission_required('sales.add_factory',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def factoryAjaxCreate(request):
    """creating vendor"""
    if request.method == 'POST':
        form = FactoryModelForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                            request, "Factory has been Added Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})



@permission_required('sales.change_factory',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def factoryAjaxUpdate(request,pk):
    """Updating vendor"""
    if request.method=='GET':
        factory=get_object_or_404(Factories,id=pk)
        return JsonResponse({'status':'success','addons':model_to_dict(factory)})

    if request.method == 'POST':
        factory= get_object_or_404(Factories,id=pk)
        form=FactoryModelForm(request.POST,instance=factory)
        if form.is_valid():
            form.save()
            messages.success(
                            request, "Factory has been Added Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})

@permission_required('sales.delete_factory',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteFactoryBulk(request):
    """deleting vendor in bulk"""
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            try:
                factory=Factories.objects.filter(id=item_id[int(i)]).delete()
                messages.success(request, "Selected factory has been removed successfully.")
            except ProtectedError as e:
                messages.error(request,'Cannot delete some factory because they have orders assigned to delivery boy.')
    return redirect(request.META['HTTP_REFERER'])

@permission_required('sales.delete_factory',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def factoryDelete(request,pk):
    """Deleting particular vendor"""
    if request.method=='POST':
        try:
            factory=get_object_or_404(Factories,id=pk).delete()
            messages.success(request, "Factory has been removed successfully.")
        except ProtectedError as e:
            messages.error(request, "Cant delete this factory because this factory has orders assigned to delivery boy.")
        return redirect('sales:factory-list')




import xlwt

from django.http import HttpResponse
from django.contrib.auth.models import User
import datetime as dt

@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def export_order_xls(request):
    from datetime import datetime
    date__range = request.GET.get('date_range',None)
    order_by_type = request.GET.get('order_by_type',None)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="order.xls"'
    order_status = request.GET.getlist('order_status', None)
    payment_status = request.GET.getlist('payment_status', None)
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('OrderItem')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['sender email',
        'sender name',
        'sender contact',
        'receiver name',
        'receiver address',
        'receiver contact',
        # 'order placed by',
        'order number',
        'total', 
        'sub total',
        'shipping cost',
        'discount',
        'order status',
        'payment status',
        'delivery status',
        'payment method',
        'date',
        'time interval start',
        'time interval end',
        'created on',
        'vendor',
        'Delivery Boy First Name',
        'Delivery Boy Last Name',
        'City',
        'Area',
        'Created By',
        'Updated By',
        'message'
    ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    if date__range:
        date__range=date__range.split('to')
        if len(date__range)>1:
            start = date__range[0].strip()
            end=date__range[1].strip()
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
                # qs=Order.objects.filter(Q(placed_on__range=[start_date,end_date]) | Q(order_status__in=order_status) | Q(payment_status__in=payment_status)) 
            if payment_status and order_status:       
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date], order_status__in=order_status, payment_status__in=payment_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date], order_status__in=order_status, payment_status__in=payment_status)
            if not payment_status and order_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date], order_status__in=order_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date], order_status__in=order_status)
            
            if payment_status and not order_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date], payment_status__in=payment_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date], payment_status__in=payment_status)
            if not payment_status and not order_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date])
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date])

            rows=rows.values_list('delivery_address__sender_email',
            'delivery_address__sender_fullname',
            'delivery_address__contact_number',
            'delivery_address__receiver_fullname',
            'delivery_address__receiver_delivery_address',
            'delivery_address__receiver_contact_number1',
            # 'items__product__product__store__name',
            'order_number',
            'total', 
            'sub_total_order',
            'shipping_cost',
            'discount',
            'order_status',
            'payment_status',
            'delivery_status',
            'payment_method',
            'date',
            'time__time_from',
            'time__time_to',
            'created_on',
            'vendor__name',
            'delivery_order__user__first_name',
            'delivery_order__user__last_name',
            'delivery_address__receiver_city',
            'delivery_address__receiver_area',
            'created_by__first_name',
            'updated_by__first_name',
            'items__special_instruction')
        else:
            start = date__range[0]
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
                # qs=Order.objects.filter(Q(placed_on=start_date) | Q(order_status__in=order_status) | Q(payment_status__in=payment_status))
            if payment_status and order_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, order_status__in=order_status, payment_status__in=payment_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, order_status__in=order_status, payment_status__in=payment_status)
            
            if order_status and not payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, order_status__in=order_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, order_status__in=order_status)
            if not order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, payment_status__in=payment_status)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, payment_status__in=payment_status)

            if not order_status and not payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date)



            rows=rows.values_list('delivery_address__sender_email',
            'delivery_address__sender_fullname',
            'delivery_address__contact_number',
            'delivery_address__receiver_fullname',
            'delivery_address__receiver_delivery_address',
            'delivery_address__receiver_contact_number1',
            # 'items__product__product__store__name',
            'order_number',
            'total',
            'sub_total_order',
            'shipping_cost',
            'discount',
            'order_status',
            'payment_status',
            'delivery_status',
            'payment_method',
            'date',
            'time__time_from',
            'time__time_to',
            'created_on',
            'vendor__name',
            'delivery_order__user__first_name',
            'delivery_order__user__last_name',
            'delivery_address__receiver_city',
            'delivery_address__receiver_area',
            'created_by__first_name',
            'updated_by__first_name',
            'items__special_instruction')

    else:
        if order_status and payment_status:
            rows = Order.objects.filter(order_status__in=order_status, payment_status__in=payment_status)
        if order_status and not payment_status:
            rows = Order.objects.filter(order_status__in=order_status)
        if not order_status and payment_status:
            rows = Order.objects.filter(payment_status__in=payment_status)
        
        if not order_status and not payment_status:
            rows = Order.objects.all()


        
        rows = rows.prefetch_related('delivery_address').values_list('delivery_address__sender_email',
            'delivery_address__sender_fullname',
            'delivery_address__contact_number',
            'delivery_address__receiver_fullname',
            'delivery_address__receiver_delivery_address',
            'delivery_address__receiver_contact_number1',
            # 'items__product__product__store__name',
            'order_number',
            'total',
            'sub_total_order',
            'shipping_cost',
            'discount',
            'order_status',
            'payment_status',
            'delivery_status',
            'payment_method',
            'date',
            'time__time_from',
            'time__time_to',
            'created_on',
            'vendor__name',
            'delivery_order__user__first_name',
            'delivery_order__user__last_name',
            'delivery_address__receiver_city',
            'delivery_address__receiver_area',
            'created_by__first_name',
            'updated_by__first_name',
            'items__special_instruction',
            )

    print(rows)
    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, dt.datetime) else x for x in row] for row in rows ]
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response

@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def export_sales_xls(request):
    from datetime import datetime
    date__range = request.GET.get('date_range',None)
    order_by_type = request.GET.get('order_by_type',None)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="order.xls"'

    order_status = request.GET.getlist('order_status', None)
    payment_status = request.GET.getlist('payment_status', None)

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('OrderItem')

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Customer',
        'Order Line / Product',
        'Order Line / Ordered Quantity',
        'Analytic Tags',
        'Price',
        ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
    if date__range:
        date__range=date__range.split('to')
        if len(date__range)>1:
            start = date__range[0].strip()
            end=date__range[1].strip()
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            end_date = datetime.strptime(end, '%Y-%m-%d').date()
                # qs=Order.objects.filter(Q(placed_on__range=[start_date,end_date]) | Q(order_status__in=order_status) | Q(payment_status__in=payment_status)) 
            if order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date],order_status__in=order_status, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date], order_status__in=order_status, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
            if order_status and not payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date],order_status__in=order_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date], order_status__in=order_status)
                    item = OrderItem.objects.filter(order__in = rows)
            
            if not order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date],payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date],payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
            
            if not order_status and not payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on__range=[start_date,end_date])
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date__range=[start_date,end_date])
                    item = OrderItem.objects.filter(order__in = rows)

            rows=item.values_list('order__delivery_address__receiver_fullname',
            'name',
            'quantity',
            'flavour',
            'price'
            )
        else:
            start = date__range[0]
            start_date = datetime.strptime(start, '%Y-%m-%d').date()
            if order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, order_status__in=order_status, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, order_status__in=order_status, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
            if order_status and not payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, order_status__in=order_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, order_status__in=order_status)
                    item = OrderItem.objects.filter(order__in = rows)
            
            if not order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date, payment_status__in=payment_status)
                    item = OrderItem.objects.filter(order__in = rows)
            if order_status and payment_status:
                if int(order_by_type) == 1:
                    rows = Order.objects.prefetch_related('delivery_address').filter(placed_on=start_date)
                    item = OrderItem.objects.filter(order__in = rows)
                if int(order_by_type) == 2:
                    rows = Order.objects.prefetch_related('delivery_address').filter(date=start_date)
                    item = OrderItem.objects.filter(order__in = rows)


            rows=item.values_list('order__delivery_address__receiver_fullname',
            'name',
            'quantity',
            'flavour',
            'price'
            )

    else:
        if order_status and payment_status:
            rows = Order.objects.filter(order_status__in=order_status, payment_status__in=payment_status).prefetch_related('delivery_address')
        if order_status and not payment_status:
            rows = Order.objects.filter(order_status__in=order_status).prefetch_related('delivery_address')
        if not order_status and payment_status:
            rows = Order.objects.filter(payment_status__in=payment_status).prefetch_related('delivery_address')
        if not order_status and not payment_status:
            rows = Order.objects.prefetch_related('delivery_address')

        item = OrderItem.objects.filter(order__in = rows)
        rows=item.values_list('order__delivery_address__receiver_fullname',
            'name',
            'quantity',
            'flavour',
            'price'
            )

    rows = [[x.strftime("%Y-%m-%d %H:%M") if isinstance(x, dt.datetime) else x for x in row] for row in rows ]
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)
    return response




from django.views.generic import DetailView,ListView,CreateView
from django.urls import reverse,reverse_lazy

class OrderToCustomer(DetailView):
    slug_url_kwarg = 'order_number'
    slug_field = 'order_number' 
    model = Order
    template_name = 'admin_view/orders/order-detail-to-customer.html'
    context_object_name = 'orders'


@permission_required('sales.view_orderalert',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderAlertList(request):
    if request.method=='GET':
        alert=OrderAlert.objects.order_by('-id')
        form=OrderAlertForm()
        return render(request,'admin_view/orders/order_alert.html',{'alert':alert,'form':form})

@permission_required('sales.add_orderalert',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderAlertAjaxCreate(request):
    if request.method == 'POST':
        form = OrderAlertForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Added Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})



@permission_required('sales.change_orderalert',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderAlertAjaxUpdate(request,pk):
    if request.method=='GET':
        alert=get_object_or_404(OrderAlert,id=pk)
        return JsonResponse({'status':'success','addons':model_to_dict(alert)})

    if request.method == 'POST':
        alert= get_object_or_404(OrderAlert,id=pk)
        form=OrderAlertForm(request.POST, instance = alert)
        if form.is_valid():
            form.save()
            messages.success(
                            request, "Updated Successfully")
            return JsonResponse({'status': 'success'})
        return JsonResponse({'errors': form.errors})

@permission_required('sales.delete_orderalert',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteOrderAlertBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            alerts=OrderAlert.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected data removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('sales.delete_orderalert',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def orderAlertDelete(request,pk):
    if request.method=='POST':
        alert=get_object_or_404(OrderAlert,id=pk).delete()
        messages.success(request, "Removed successfully.")
        return redirect('sales:order-alert-list')

@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def canceledOrders(request):
    if request.method == 'GET':
        order_keyword = request.GET.get('order_keyword',None)
        order = Order.objects.filter(order_status='Cancelled')
        if order_keyword:
            order = order.filter(order_number__icontains = order_keyword)
       
        paginator = Paginator(order, 50)
        try:
           page_number = request.GET.get('page')
           if page_number is None:
               page_number=1
           order = paginator.get_page(page_number)
        except PageNotAnInteger:
           order = paginator.get_page(1)
        except EmptyPage:
           order = paginator.get_page(paginator.num_pages)

        return render(request, 'admin_view/orders/cancelled_order.html', {'order_list':order,'order_keyword':order_keyword, 'page_number':page_number})

from djqscsv import render_to_csv_response
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def export_order_logs_to_csv(request):
    order_id = request.GET.get('order_id', None)
    if order_id:
        qs = OrderLogs.objects.filter(order_id=order_id).values('order__order_number','log_created_by__first_name','log_created_by__last_name','created_at','order_data_log','order_item','addons')
    else:
        qs = OrderLogs.objects.all().values('order__order_number','log_created_by__first_name','log_created_by__last_name','created_at','order_data_log','order_item','addons')
    return render_to_csv_response(qs)


def all_order_push_odo(request):
    # start_date = "2022-07-17"
    # end_date = "2022-08-05"
    orders = Order.objects.order_by("-id").exclude(odoo_status="Success").values('id', 'order_number')[:100]
    order_pass_list = []
    try:
        for ids in orders:
            order_id = ids['id']
            order_number = ids['order_number']
            rider = OrderDelivery.objects.filter(order__order_number=order_id).values('user__username', 'user__profile__phone_number', 'user__email')
            if rider:
                rider_name = rider[0].get('user__username')
                rider_phone = rider[0].get('user__profile__phone_number')
                rider_email = rider[0].get('user__email')
            else:
                rider_name = None
                rider_phone = None
                rider_email = None
            try:
                order_pass, error = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, request.user.username,request.user.email)
                print(order_pass)
                Order.objects.filter(id=order_id).update(odoo_status=order_pass)
            except Exception as e:
                return HttpResponse(str(e))
        return HttpResponse("Success")
    except Exception as e:
        return HttpResponse(str(e))

# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
def push_all_failed_order_to_odoo(request):
    date = "2022-07-17"
    order_detail_count = OrderItem.objects.filter(order__created_on__gte=date, order__order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).exclude(order__odoo_status__in=["Finished"]).order_by("-id").count()
    try:
        date = "2022-07-17"
        order_detail = OrderItem.objects.filter(order__created_on__gte=date,  order__order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).exclude(order__odoo_status__in=["Finished"]).order_by("-id").values('order__id')[:30]
        status_list = []
        if order_detail:
            for i in order_detail:
                try:
                    order_id = i['order__id']
                    rider = OrderDelivery.objects.filter(order__id=order_id).values('user__username', 'user__profile__phone_number', 'user__email')
                    if rider:
                        rider_name = rider[0].get('user__username')
                        rider_phone = rider[0].get('user__profile__phone_number')
                        rider_email = rider[0].get('user__email')
                    else:
                        rider_name = None
                        rider_phone = None
                        rider_email = None
                    status, error = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, "Santosh", "santosh@ohocake.com")
                    status_list.append({"status":status, "error":error, "id":order_id})
                    ord = Order.objects.filter(id=order_id).update(odoo_status=status)
                except Exception as e:
                   return JsonResponse({"error":str(e), "order_id":order_detail_count})
            return JsonResponse({"status":status_list, "count":order_detail_count})
        else:
            return HttpResponse("No Error Case Till Now")
    except Exception as e:
        return JsonResponse({"error":str(e), "count":order_detail_count})


def push_order_list_odoo(request):
    o_number = ["2022-01-02-40","2023-01-07-30","2023-01-11-33", "2023-01-07-33","2023-01-08-29","2023-01-11-14","2023-01-01-10","2023-01-13-24","2023-01-13-17",			
            "2023-01-13-8","2023-01-14-22","2022-08-06-44",	"2022-08-07-29","2022-08-10-38","2022-08-09-31","2022-08-13-27","2023-01-18-29","2023-01-18-31",			
            "2023-01-16-47","2023-01-17-39","2023-01-18-6",	"2023-01-17-13","2023-01-10-44", "2023-01-19-32","2023-01-23-15","2023-01-21-21",			
            "2022-12-22-42","2022-12-23-23","2022-12-27-35","2023-01-21-30","2023-01-25-36","2023-01-26-44","2023-01-29-1","2023-01-31-31"]
    status_list = []
    for i in o_number:
        try:
            order_detail = Order.objects.filter(order_number=i,odoo_status__in=["Failed", "None"]).get()
            if order_detail:
                try:
                    order_id = order_detail.id
                    rider = OrderDelivery.objects.filter(order__id=order_id).values('user__username')
                    if rider:
                        rider_name = rider[0].get('user__username')
                    else:
                        rider_name = None
                    status, error = sendOrderToOdoo(order_id, rider_name)
                    status_list.append({status:error})
                    ord = Order.objects.filter(id=order_id).update(odoo_status=status)
                except Exception as e:
                    return HttpResponse(str(e))
        except:
            pass
    return HttpResponse(status_list)

