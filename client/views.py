from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from catalog.models import *
from settings.models import *
from sales.models import *
from .models import *
from datetime import date, datetime, timezone, timedelta
import datetime as dt
from django.db.models import Q, Avg, Max, Min
import secrets
from django.urls import reverse_lazy
from sales.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from payment.models import *
from sales.sparrow import *
from django.conf import settings as conf
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from utility.hostname import *
from django.contrib import messages
from accounts.forms import ChangePasswordUserForm
from utility.send_email import send_email_to_user
from django.core.validators import validate_email
from marketing.models import CartCoupon
from NewsletterandContact.forms import ContactForm, SubscriptionForm
from .utils import *
from store.models import Location as StoreLocation
from sentry_sdk import capture_exception
from store.models import StoreReview
from landing.models import *
import uuid
from client.custom_decorator import *
from django.db.models.functions import Coalesce


def trigger_error(request):
    division_by_zero = 1 / 0

import pdb


@method_decorator(csrf_exempt, name='dispatch')
class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(BaseView, self).get_context_data(**kwargs)
        location_slug = self.request.GET.get('store_locations', None)
        update_new_location(location_slug,self.request)
        try:
            settings = Settings.objects.first()
            currency = settings.currency
            minimum_order_price = settings.minimum_order_price
        except Settings.DoesNotExist:
            currency = "Rs"
            settings = ""
            minimum_order_price = 0

        context['store_locations'] = StoreLocation.objects.filter(parent=None,is_active=True)
        context['subscriptionform'] = SubscriptionForm()
        # context['locations'] = Location.objects.all()
        context['minimum_order_price'] = minimum_order_price
        context['currency'] = currency
        context['settings'] = settings
        context['category'] = Category.objects.filter(parent=None, is_available=True,is_type=True).order_by('display_order')
        context['category_badge'] = Category.objects.filter(is_available=True,show_on_landing=True).order_by('display_order')[:6]
        context['occasion'] = Category.is_occasion()
        context['flavour'] = Flavour.objects.all()
        return context


@method_decorator(csrf_exempt, name='dispatch')
class CatalogView(BaseView):
    template_name = 'client/cake-977/index.html'
    def get_context_data(self, **kwargs):
        context = super(CatalogView, self).get_context_data(**kwargs)
        context['section_one']=SectionOne.get_section_one_items(self.request)
        context['landing_categories']=LandingCategories.get_landing_categories(self.request)
        context['landing_banner']=LandingFullBanner.get_section_four_banner_items(self.request)
        context['popular_flavour'] = PopularFlavourSection.get_popular_flavours(self.request)
        context['best_seller'] = BestSellersSection.get_best_seller_products(self.request)
        context['recomended'] = Product.objects.filter(is_recomended=True, is_available=True)[:10]
        # context['active_store'] = ExploreStore.get_store(self.request)
        return context

    

from smarttech_payment_api.models import KhaltiCredential,EsewaCredential,IMEPaymentCredential,NICCredential
class CheckoutCartView(BaseView):
    template_name = 'client/cake-977/cart.html'
    def get_context_data(self, **kwargs):
        context=super(CheckoutCartView,self).get_context_data(**kwargs)
        location=Location.get_store_location_obj(self.request)
        sub_location=location.get_children().filter(is_active=True)
        try:
            area=sub_location[0].get_children().filter(is_active=True)
        except:
            area=''
        context['sub_location']=sub_location
        context['sub_location_area']=area
        context['khalti'] = KhaltiCredential.objects.last()
        context['esewa'] = EsewaCredential.objects.last()
        context['ime'] = IMEPaymentCredential.objects.last()
        context['nic'] = NICCredential.objects.last()
        if not self.request.user.is_authenticated:
            context['cart_count'] = 0
            try:
                if self.request.session.values():
                    data = sessionCalculation(self.request)
                    cart_list = data.get('cart_list')
                    sub_total = data.get('sub_total')
                    total = data.get('total')
                    cart_count = data.get('cart_count')
                    total_with_shipping_method = data.get('total_with_shipping_method')
                    shipping_cost_total = data.get('shipping_cost_total')
                    discounted_total=data.get('discounted_total')
                    context['discounted_sub_total']=data.get('discounted_sub_total')
                    context['coupon'] = data.get('coupon')
                    context['is_unique_item_only']=data.get('is_unique_item_only')
                    context['cart_list'] = cart_list
                    context['cart_count'] = cart_count
                    context['discounted_total'] = discounted_total
                    context['sub_total'] = sub_total
                    context['total_without_shipping_cost'] = data.get('total_without_shipping_cost')
                    context['total_with_shipping_method'] = total_with_shipping_method
                    context['shipping_cost_total'] = shipping_cost_total
                return context

            except Exception as e:
                total = 0
                total1 = None
                coupon = None
                context['coupon'] = None
                context['cart_list'] = None
                context['cart_count'] = 0
                context['discounted_total'] = 0
                return context

        if self.request.user.is_authenticated:
            try:
                Cart.objects.get(user=self.request.user)
            except:
                Cart.objects.create(user=self.request.user)
            cart = get_object_or_404(Cart, user=self.request.user)
            
            total_with_shipping_method = cart.get_total_with_shipping_method()
            context['cart_list'] = cart.cart_list
            context['is_unique_item_only']=cart.is_unique_item_only
            context['coupon'] = cart.coupon
            context['cart_count'] = cart.cart_count()
            context['discounted_total'] = cart.discounted_total
            context['discounted_sub_total'] = cart.discounted_sub_total()
            context['sub_total'] = cart.get_sub_total()
            context['total_without_shipping_cost'] = cart.get_sub_total()
            context['total_with_shipping_method'] = cart.get_total_with_shipping_method()
            context['shipping_cost_total'] = cart.get_shipping_price_total()
            
            return context

    def get(self, request, *args):
        return super(CheckoutCartView, self).get(request)

    def post(self, request):

        updateCouponInCartOrSession(self.request)
        product = int(request.POST.get('product', None))
        product_varient = request.POST.get('varient', None)
        quantity = request.POST.get('quantity', 1)
      
        addons = request.POST.getlist('addons', None)
        addons_quantity = request.POST.getlist('addons_quantity', None)
        while ("" in addons_quantity):
            addons_quantity.remove("")
            addons.remove("")
        date_delivery = request.POST.get('delivery_date', None)
        time = str(request.POST.get('time',None))
        if not time:
            return JsonResponse({'error':'Please select time.'})
        message = request.POST.get('message', None)
        redirect_to_checkout = request.POST.get('redirect_to_checkout', '')
        is_eggless = request.POST.get('is_eggless', None)
        is_sugarless = request.POST.get('is_sugarless', None)
        pound = request.POST.get('pound', None)
        shipping_method = int(request.POST.get('shipping_method_id',None))
        photo_for_photo_cake = request.FILES.get('photo_for_photo_cake',"")

        product_ = get_object_or_404(Product, id=product)
        varient_ = get_object_or_404(ProductVarient, id=product_varient)
        
        # if not varient_.quantity < 1 and not varient_.quantity < int(quantity) and int(quantity) >= 1:
        if int(quantity):
            if not self.request.user.is_authenticated:
                unique_id = str(uuid.uuid4())
                distinct_order_keys=str(product_.store.slug)+str(date_delivery)+str(time)
                menu = []
                menu.append(
                    MenuItem1(distinct_order_keys,product, varient_.id, quantity, addons, addons_quantity, date_delivery, time, message,
                              pound, is_eggless, is_sugarless, shipping_method,unique_id).serialize())
                key = str(product) + str(varient_.id) + str(date_delivery) + str(time)

                response = addToSession(request,key,quantity,varient_,product,addons,addons_quantity,date_delivery,time,message,pound,is_eggless,is_sugarless,shipping_method,unique_id,menu,distinct_order_keys)
                if response == "error":
                    return JsonResponse({'error': 'Selected quantity is not available on stock'})
                
                SessionImage.store_session_image(unique_id,photo_for_photo_cake)
                data = sessionCalculation(self.request)
                cart_count = data.get('cart_count')
                return JsonResponse({'status': 'Success','redirect_to_checkout': redirect_to_checkout,'cart_count':cart_count})
            
            if self.request.user.is_authenticated:
                cart = Cart.objects.get(user=self.request.user)
                shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
                varient = get_object_or_404(ProductVarient, id=product_varient)
                CartItem.addToCart(cart, varient_, date_delivery, time, is_eggless, is_sugarless, message,
                                   shipping_method, pound, quantity, addons, addons_quantity,photo_for_photo_cake)
                return JsonResponse({'status': 'Success','redirect_to_checkout': redirect_to_checkout,'cart_count':cart.cart_count()})
                
        else:
            return JsonResponse({'error': 'Selected quantity is not available on stock'})


def check_product_location(request,product,product_selected_location):
    location_obj = get_object_or_404(StoreLocation, slug=product_selected_location)
    StoreLocation.store_location_id_in_session(request,location_obj.id)
    if (Store.objects.filter(location=location_obj,store_product=product).exists()):
        return True
    else:
        return False
    
class ProductDetailView(BaseView):
    template_name = 'client/cake-977/product_detail.html'
    
    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'],store__is_active=True)
        product_selected_location = request.GET.get('store_locations',None)
        if product_selected_location:
            result = check_product_location(request,product,product_selected_location)
            return redirect(request.META['HTTP_REFERER']) if result else redirect('client:catalog')
        
        allow_review_status=Product.allowReview(request,product)
        is_reviewed=Product.is_reviewed(request,product)
        star_count=ProductReview.get_star_count(product)
        star_percentage = ProductReview.get_star_percentage(product)
        get_total_user_product_ratings=ProductReview.get_total_user_product_ratings(product)
        get_average_rating_product=ProductReview.get_average_rating_product(product)
        get_ratings=ProductReview.get_ratings(product)
        related_product = product.get_related_products
      

        shipping_metehod = ShippingMethod.get_shipping_method(product)
        product_varients = ProductVarient.objects.filter(product=product,status=True,quantity__gte=1).order_by('display_order_varient')
        first_varient = product_varients.first()
        try:
            varient_obj = get_varient_obj(product_varients) if get_varient_obj(product_varients) else []
            return super(ProductDetailView, self).get(request, product=product,first_varient=first_varient,
                varient_obj=varient_obj,shipping_method=shipping_metehod,
                star_count=star_count,get_total_user_product_ratings=get_total_user_product_ratings,
                get_ratings=get_ratings,get_average_rating_product=get_average_rating_product,star_percentage=star_percentage,related_product=related_product,allow_review_status=allow_review_status,is_reviewed=is_reviewed)
        except Exception as e:
            print('detail page exception')
            # capture_exception(e)
            return super(ProductDetailView, self).get(request, product=product,first_varient=first_varient,shipping_method=shipping_metehod,star_count=star_count,
                                                      get_total_user_product_ratings=get_total_user_product_ratings,get_ratings=get_ratings,
                                                      get_average_rating_product=get_average_rating_product,star_percentage=star_percentage,related_product=related_product,allow_review_status=allow_review_status,is_reviewed=is_reviewed)


def get_varient_obj(product_varients):
    varient_obj = []
    for item  in product_varients:
        if item.attribut_value.filter(attribute__name='Weight').exists():
            first_attr_names='Weight'
        elif item.attribut_value.filter(attribute__name='Quantity').exists():
            first_attr_names='Quantity'
        else:
            first_attr_names=False
        if item.attribut_value.filter(attribute__name='Flavour').exists():
            second_attr_names='Flavour'
        else:
            second_attr_names=False
            
        attributes = []
        if first_attr_names:
            varient_attributes1 = AttributeValue.objects.filter(attribute_value=item,attribute_value__status=True,attribute__name=first_attr_names,attribute_value__quantity__gte=1)
            attributes1 = [attr.value for attr in varient_attributes1]
        else:
            attributes1=[]
        if second_attr_names:
            varient_attributes2 = AttributeValue.objects.filter(attribute_value=item,attribute_value__status=True,attribute__name=second_attr_names,attribute_value__quantity__gte=1)
            attributes2 = [attr.value for attr in varient_attributes2]
        else:
            attributes2=[]
        attributes=attributes1+attributes2
        discount_percentage = item.discount() if item.discount() else ""
        old_price = item.old_price if not item.selling_price >= item.old_price else "" 
        varient_obj.append({'varient_id':item.id,'attribute':attributes,'selling_price':item.selling_price,'old_price':old_price,'discount':discount_percentage})
    return varient_obj
    

def cartQuantityUpdate(request):
    if request.method == 'POST':
        updateCouponInCartOrSession(request)
        product_varient = request.POST.get('varient', None)
        quantity = request.POST.get('quantity', None)
        delivery_date = request.POST.get('delivery_date', None)
        total_quantity_varient=request.POST.get('total_quantity_varient',None)
        time = request.POST.get('time', None)
        varient=ProductVarient.objects.get(id=product_varient)
        product = varient.product.id
        if not request.user.is_authenticated:
            key = str(product) + str(product_varient) + str(delivery_date) + str(time)
            
            if int(quantity) <= 0:
                del request.session[str(key)]
                cart_count=sessionCalculation(request).get('cart_count')
                return JsonResponse({'status': 'Success','cart_count':cart_count})
            else:
                # can be used later, to check quantity validation
                # if int(total_quantity_varient) <= varient.quantity:                    
                #     if ProductVarient.objects.get(id=product_varient).quantity < int(quantity):
                #         return JsonResponse({'error': 'Quantity unavailable.'})
                #     else:
                #         request.session[str(key)][0].update(quantity=quantity)
                #     cart_count=sessionCalculation(request).get('cart_count')
                #     return JsonResponse({'status': 'Success','cart_count':cart_count})
                # return JsonResponse({'error': 'Selected quantity is not available.'})

                # without checking stock
                request.session[str(key)][0].update(quantity=quantity)
                cart_count=sessionCalculation(request).get('cart_count')
                return JsonResponse({'status': 'Success','cart_count':cart_count})
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            if int(quantity) < 1:
                try:
                    CartItem.objects.get(cart=cart, product=product_varient, date=delivery_date, time=time).delete()
                    return JsonResponse({'status': 'Success','cart_count':cart.cart_count(),'total_payable_amount': str(cart.discounted_total())})
                except:
                    return JsonResponse({'error': 'Item doesnot exist.'})
            else:
                # if int(total_quantity_varient) <= varient.quantity:
                if int(quantity):
                    CartItem.objects.filter(cart=cart, product=product_varient, date=delivery_date, time=time).update(
                            quantity=quantity)
                    return JsonResponse({'status': 'Success','cart_count':cart.cart_count(),'total_payable_amount': str(cart.discounted_total())})
                return JsonResponse({'error': 'Selected quantity is not available.'})

@login_required
def applyCoupon(request):
    if request.method == "POST":
        coupon_number = str(request.POST.get('coupon', None))
        response=CartCoupon.totalToApplyCoupon(request)
        if response.get('error')== True:
            return JsonResponse({'error': 'No item in your cart.', 'coupon': coupon_number})
        total=response.get('total')
        cart_count=response.get('cart_count')
        try:
            coupon = CartCoupon.objects.get(coupon_number=coupon_number, is_active=True)
            current_time = datetime.datetime.now().date()
            coupon_per_user_limit = coupon.per_user_limit
            coupon_limit = coupon.total_user_limit
            min_cart_amount = coupon.min_cart_price
            max_cart_amount = coupon.max_cart_price
            time_limit = coupon.time_limit

            user_coupon_count=Order.objects.filter(~Q(order_status='Cancelled'),customer=request.user,coupon=coupon).count()
            coupon_total_used = Order.objects.filter(~Q(order_status='Cancelled'), coupon=coupon).count()

            check_time_validity = current_time < time_limit
            check_price_range_validity = min_cart_amount <= total <= max_cart_amount
            check_user_per_limit_validity=user_coupon_count<coupon_per_user_limit
            check_total_coupon_limit_validity = coupon_total_used < coupon_limit
            if check_time_validity and check_price_range_validity and check_total_coupon_limit_validity and check_user_per_limit_validity:
                response=CartCoupon.getTotalAfterCouponApply(request,coupon.coupon_number,total)
                total=response.get('total')
                previous_total=response.get('previous_total')
                return JsonResponse({'status': 'Success', 'coupon': model_to_dict(coupon)})
            else:
                return JsonResponse(
                    {'error': 'Cart requirement unfulfilled.', 'coupon': coupon_number, 'min_value': min_cart_amount,
                     'max_value': max_cart_amount, 'validity_date': coupon.time_limit})
        except:
            return JsonResponse({'error': 'Invalid Coupon.', 'coupon': coupon_number})


def placeOrder(request):
    response = place_normal_order(request)
    if response['status'] == "error":
        return JsonResponse({'error':response['message']})
    else:   
        return JsonResponse({'status':'success','reference':response['reference']})
    
def place_normal_order(request):
    if request.method=='POST':
        i_am_receiver=request.POST.get('i_am_receiver',False)
        receiver_fullname=request.POST.get('receiver_fullname',None)
        receiver_email=request.POST.get('receiver_email',None)
        receiver_address=request.POST.get('receiver_address',None)
        landmark=request.POST.get('landmark',None)
        address_type=request.POST.get('address_type',None)
        receiver_number1=request.POST.get('receiver_number1',None)
        receiver_number2=request.POST.get('receiver_number2',None)
        occasion=request.POST.get('occasion',None)
        sender_full_name=request.POST.get('sender_full_name',None)
        sender_phone_number=request.POST.get('sender_phone_number',None)
        sender_address=request.POST.get('sender_address',None)
        sender_email=request.POST.get('sender_email',None)

        area=request.POST.get('area',None)
        city=request.POST.get('city',None)
        hide_info_from_receiver=request.POST.get('hide_info_from_receiver',False)
        # payment_method = request.POST.get('payment_method', '')
        payment_method='COD'
        return_object = {}

        i_am_receiver = True if i_am_receiver else False
        hide_info_from_receiver = True if hide_info_from_receiver else False
        response = validate_order_request(receiver_fullname,receiver_address,receiver_number1,sender_full_name,sender_phone_number,receiver_email,sender_email,payment_method,sender_address,city,area)
        if response:
            return_object['status'] = "error"
            return_object['message'] = response
            return return_object

        settings_object = Settings.objects.all().get()
        response=validate_cart_quantity(request,settings_object)
        if response:
            return_object['status'] = "error"
            return_object['message'] = response
            return return_object
        
        user_obj = request.user if request.user.is_authenticated else None
        address=DeliveryAddress.createDeliveryAddress(user_obj,i_am_receiver,receiver_fullname,
            receiver_email,receiver_address,landmark,address_type,receiver_number1,
            receiver_number2,occasion,sender_full_name,sender_phone_number,sender_email,hide_info_from_receiver,sender_address,city,area)
        
        if address:
            if not request.user.is_authenticated:
                response=placeOrderUnauth(request,user_obj,address)
                return_object['status'] = "Success"
                return_object['reference'] = response.get('reference')
                return return_object
        
            if request.user.is_authenticated:
                cart=get_object_or_404(Cart,user=request.user)

                cart_item=CartItem.objects.filter(cart=cart).order_by('product__product__store','date','time').distinct('product__product__store','date','time')
                reference=secrets.token_hex(3)
                if Order.objects.filter(reference=reference).exists():
                    reference=reference+secrets.token_hex(1)
                
                for item in cart_item:
                    sub_total = item.discounted_sub_total_
                    total=item.discounted_total_
                    # order_number=secrets.token_hex(3)
                    # if Order.objects.filter(order_number=order_number).exists():
                    #     order_number=order_number+secrets.token_hex(1)
                    order_number = order_number_by_date()
                    shipping_cost=item.total_shipping_cost_
                    discount=cart.discount
                    coupon=cart.coupon
                    
                    date=item.date
                    time=get_object_or_404(ShippingTime,id=item.time)
                    order=Order.placeOrderAuth(user_obj,order_number,discount,coupon,sub_total,shipping_cost,address,total,cart,item,reference,date,time)
                    
                cart.coupon=None
                cart.save()
                CartItem.objects.filter(cart=cart).delete()
                        
                return_object['status'] = "Success"
                return_object['reference'] = reference
                return return_object
                
        else:
            return_object['status'] = "error"
            return_object['message'] = "Enter your address."
            return return_object


class OrderSuccess(BaseView):
    template_name = 'client/cake-977/order_success.html'

    def get(self, request, *args, **kwargs):
        reference = self.kwargs['reference']
        order = Order.objects.filter(reference=reference)
        return super(OrderSuccess, self).get(request, order=order)


class StoreList(BaseView):
    template_name = 'client/cake-977/shop_wise_list.html'

    def get(self, request, *args, **kwargs):
        filter_value = request.GET.get('filter', None)
        location = StoreLocation.get_store_location_obj(request)
        if filter_value=='rated':
            stores = Store.objects.filter(is_active=True,location=location).prefetch_related('location').annotate(store_average_review=Coalesce(Avg('store_review__review_star'),0)).order_by('-store_average_review')
        else:
            stores = Store.objects.filter(is_active=True,location=location).prefetch_related('location')
        paginator = Paginator(stores, 8)
        try:
            page = request.GET.get('page')
            stores = paginator.get_page(page)
        except PageNotAnInteger:
            stores = paginator.get_page(1)
        except EmptyPage:
            stores = paginator.get_page(paginator.num_pages)
        return super(StoreList, self).get(request, stores=stores,filter_value=filter_value)


def send_email_ajax(request):
    settings_object = Settings.objects.all().get()
    contact_number = settings_object.contact_number
    reference = request.GET.get('reference', None)
    reference = Order.objects.filter(reference=str(reference))
    baseurl = hostname_from_request(request)
    for order in reference:
        if conf.LIVE:
            # Sparrow SMS
            try:
                vendor_number = str(contact_number)[-10:]
                message = "You have received new order from " + str(order.delivery_address.receiver_fullname)[
                                                                -15:] + ". Order ID: " + str(
                    order.order_number) + ".Total Amt: " + str(
                    order.total) + ".For details please check your Dashboard."
                send_order_sms("InfoSMS", vendor_number, str(message)[:155])
                pass

            except Exception as e:
                capture_exception(e)
                pass       
        setting_ = Settings.objects.all().get()
        currency = setting_.currency

        send_email_to_user(subject_name="Thank you for your order", to_email=str(order.delivery_address.sender_email                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            ),
                           obj={'order': order, 'setting': setting_,'currency': currency,
                            'base_url': baseurl}, template_location="email_templates/order_placed.html")
    return JsonResponse({})


def get_shipping_method(request):
    if request.method == "GET":
        selected_date = request.GET.get('selected_date',None)
        product_id = request.GET.get('product_id',None)
        product = Product.objects.get(id=int(product_id))
        response = ShippingMethod.get_filtered_shipping_method(selected_date,product)
        return JsonResponse({'response':response})
        
        
class CategoryProduct(BaseView):
    template_name = 'client/cake-977/list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)
        filter_by_flavour=request.GET.get('flavour_quick','')
        # filter_by_occasion=request.GET.get('occasion_quick','')
        # filter_by_category=request.GET.get('category_quick','')
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        cat_descendants = category.get_descendants(include_self=True).filter(is_available=True)
        cat_all_children = category.get_descendants(include_self=False).filter(is_available=True)
        location = StoreLocation.get_store_location_obj(request)
        products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
                                              category__in=cat_descendants).prefetch_related('flavour','store','tags','category').distinct().order_by('display_order')
        flavour_quick=Product.quickFlavour(products)
        # occasion_quick=Product.quickOccasion(products)
        # category_quick=Product.quickCategory(products)

        if filter_value == "price-hl":
            products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
                                              category__in=cat_descendants).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).prefetch_related('flavour','store','tags','category').distinct().order_by('-max_price','-max_price_2')
        elif filter_value == "price-lh":
            products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
                                              category__in=cat_descendants).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).prefetch_related('flavour','store','tags','category').distinct().order_by('max_price','max_price_2')
        elif filter_value == 'rating':
            
            products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
                                              category__in=cat_descendants).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).prefetch_related('flavour','store','tags','category').distinct().order_by('-product_review__review_star')
        elif filter_by_flavour:
            products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
                                              category__in=cat_descendants,flavour__slug=filter_by_flavour).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).prefetch_related('flavour','store','tags','category').distinct().order_by('-product_review__review_star')
        # elif filter_by_occasion:
        #     products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
        #                                       category__in=cat_descendants,category__slug=filter_by_occasion).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).prefetch_related(
        #         'tags').distinct().order_by('-product_review__review_star')
        # elif filter_by_category:
        #     products = Product.objects.filter(store__is_active=True, is_available=True,store__location=location,
        #                                       category__in=cat_descendants,category__slug=filter_by_category).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).prefetch_related(
        #         'tags').distinct().order_by('-product_review__review_star')

        else:
            products = products
        
        
        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)
        return super(CategoryProduct, self).get(request, category_=category,products_=products, slug=self.kwargs['slug'],
                                                cat_all_children=cat_all_children,
                                                filter_value=filter_value, page=page,flavour_quick=flavour_quick,filter_by_flavour=filter_by_flavour,
                                                # occasion_quick=occasion_quick,filter_by_occasion=filter_by_occasion,category_quick=category_quick,filter_by_category=filter_by_category)
                                                )

class LocationProduct(BaseView):
    template_name = 'client/cake-977/location_list.html'

    def get(self, request, *args, **kwargs):

        location_slug = request.GET.get('store_locations', None)
        filter_value = request.GET.get('filter', None)
        location = get_object_or_404(StoreLocation, slug=location_slug)
        StoreLocation.store_location_id_in_session(request,location.id)

        if filter_value == "price-hl":
            products = Product.objects.filter(Q(store__location__slug=location_slug) & Q(store__is_active=True) & Q(
                is_available=True)).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')

        elif filter_value == "price-lh":

            products = Product.objects.filter(Q(store__location__slug=location_slug) & Q(store__is_active=True) & Q(
                is_available=True)).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
        elif filter_value == "rating":
            products = Product.objects.filter(Q(store__location__slug=location_slug) & Q(store__is_active=True) & Q(
                is_available=True)).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        else:
            products = Product.objects.filter(store__location__slug=location_slug, store__is_active=True,
                                              is_available=True).distinct()
        
        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(LocationProduct, self).get(request, location=location, products=products,
                                                filter_value=filter_value, location_slug=location_slug, page=page)


class PriceRangeList(BaseView):
    template_name = 'client/cake-977/price_range_list.html'

    def get(self, request, *args, **kwargs):

        filter_by_flavour=request.GET.get('flavour_quick',None)
        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)

        filter_value = request.GET.get('filter', None)
        location = StoreLocation.get_store_location_obj(request)
        products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
        flavour_quick=Product.quickFlavour(products)

        if filter_value == "price-hl" and min_price and max_price:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True) & Q(store__location=location)).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')

        elif filter_value == "price-lh" and min_price and max_price:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True)& Q(store__location=location)).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
        
        elif filter_value == "rating" and min_price and max_price:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True) & Q(store__location=location)).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        elif filter_by_flavour:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True) & Q(store__location=location),flavour__slug=filter_by_flavour).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')

        else:
            products = products        

        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(PriceRangeList, self).get(request, products=products, filter_value=filter_value, page=page,
                                               min_price=min_price, max_price=max_price,flavour_quick=flavour_quick,filter_by_flavour=filter_by_flavour)


class FlavourProductList(BaseView):
    template_name = 'client/cake-977/flavour_product_list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)
        flavour = get_object_or_404(Flavour, slug=self.kwargs['slug'])
        
        location = StoreLocation.get_store_location_obj(request)
       
        if filter_value == "price-hl":
            products = Product.objects.filter(
                Q(flavour__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).prefetch_related('flavour','store','tags','category').distinct().annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
        elif filter_value == "price-lh":
            products = Product.objects.filter(
                Q(flavour__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).prefetch_related('flavour','store','tags','category').distinct().annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
        elif filter_value == "rating":
            products = Product.objects.filter(
                Q(flavour__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).prefetch_related('flavour','store','tags','category').distinct().annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by(
                '-product_review__review_star')
        else:
            products = Product.objects.filter(
                Q(flavour__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).prefetch_related('flavour','store','tags','category').distinct().distinct().order_by('display_order')

        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)
        
        return super(FlavourProductList, self).get(request, flavour_=flavour, products=products,
                                                   filter_value=filter_value, page=page)


class OccasionProductList(BaseView):
    template_name = 'client/cake-977/occasion_product_list.html'

    def get(self, request, *args, **kwargs):
        filter_value = request.GET.get('filter', None)
        filter_by_flavour=request.GET.get('flavour_quick','')
        # filter_by_occasion=request.GET.get('occasion_quick','')
        # filter_by_category=request.GET.get('category_quick','')
        occasion = Occasion.objects.get(slug=self.kwargs['slug'])
        location = StoreLocation.get_store_location_obj(request)
        products = Product.objects.filter(
                Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).distinct().order_by('display_order')

        flavour_quick=Product.quickFlavour(products)
        # occasion_quick=Product.quickOccasion(products)
        # category_quick=Product.quickCategory(products)
        if filter_value == "price-hl":
            products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
        elif filter_value == "price-lh":
            products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
        elif filter_value == "rating":
            products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        
        elif filter_by_flavour:
            products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location,flavour__slug=filter_by_flavour).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        # elif filter_by_occasion:
        #     products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
        #         store__is_active=True),store__location=location,category__slug=filter_by_occasion).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        # elif filter_by_category:
        #     products = Product.objects.filter(Q(occasion__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
        #         store__is_active=True),store__location=location,category__slug=filter_by_category).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        else:
            products = products

        
        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(OccasionProductList, self).get(request,products=products,
                                                    filter_value=filter_value,occasion_=occasion, page=page,flavour_quick=flavour_quick,filter_by_flavour=filter_by_flavour,
                                                    occasion_quick=occasion_quick,filter_by_occasion=filter_by_occasion,category_quick=category_quick,filter_by_category=filter_by_category)


class StoreProductList(BaseView):
    template_name = 'client/cake-977/store_product_list.html'

    @valid_store_location_only
    def get(self, request, *args, **kwargs):
        filter_by_flavour=request.GET.get('flavour_quick',None)
        filter_by_occasion=request.GET.get('occasion_quick',None)
        filter_by_tags=request.GET.get('tags_quick',None)
        if filter_by_occasion:
            print(filter_by_occasion,filter_by_tags)

        filter_value = request.GET.get('filter', None)
        store = get_object_or_404(Store, slug=self.kwargs['slug'])
        star_count=StoreReview.get_star_count(store)
        star_percentage = StoreReview.get_star_percentage(store)
        get_total_user_store_ratings=StoreReview.get_total_user_store_ratings(store)
        get_average_rating_store=StoreReview.get_average_rating_store(store)
        get_ratings=StoreReview.get_ratings(store)
        location = StoreLocation.get_store_location_obj(request)
        products = Product.objects.filter(
                Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True),store__location=location).distinct().order_by('display_order')
        flavour_quick=Product.quickFlavour(products)
        occasion_quick=Product.quickOccasion(products)
        category_quick=Product.quickCategory(products)
        tags_quick=Product.quickTagsFilter(products)
        if filter_value == "price-hl":
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
        elif filter_value == "price-lh":
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
        elif filter_value == "rating":
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
        elif filter_by_flavour:
            # products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
            #     store__is_active=True),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            # products=products.filter(Q(flavour__slug=filter_by_flavour) | Q(tags__name=filter_by_tags) | Q(category__slug=filter_by_occasion))
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location,flavour__slug=filter_by_flavour).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            
            if filter_by_tags and filter_by_occasion:
                
                products=products.filter(tags__name=filter_by_tags,category__slug=filter_by_occasion)
            elif filter_by_tags and not filter_by_occasion:
                
                products=products.filter(tags__name=filter_by_tags)
            elif not filter_by_tags and filter_by_occasion:
                
                products=products.filter(category__slug=filter_by_occasion)
            else:
                
                products=products

        elif filter_by_occasion:
            
            # products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
            #     store__is_active=True),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            # products=products.filter(Q(flavour__slug=filter_by_flavour) | Q(tags__name=filter_by_tags) | Q(category__slug=filter_by_occasion))
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location,category__slug=filter_by_occasion).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            if filter_by_tags and filter_by_flavour:
                products=products.filter(tags__name=filter_by_tags,falvour__slug=filter_by_flavour)
            elif filter_by_tags and not filter_by_flavour:
                products=products.filter(tags__name=filter_by_tags)
            elif not filter_by_tags and filter_by_flavour:
                products=products.filter(flavour__slug=filter_by_flavour)
            else:
                products=products
        elif filter_by_tags:
            
            # products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
            #     store__is_active=True),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            # products=products.filter(Q(flavour__slug=filter_by_flavour) | Q(tags__name=filter_by_tags) | Q(category__slug=filter_by_occasion))
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True),store__location=location,tags__name=filter_by_tags).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            if filter_by_occasion and filter_by_flavour:
                products=products.filter(category__slug=filter_by_occasion,falvour__slug=filter_by_flavour)
            elif filter_by_occasion and not filter_by_flavour:
                products=products.filter(category__slug=filter_by_occasion)
            elif not filter_by_occasion and filter_by_flavour:
                products=products.filter(flavour__slug=filter_by_flavour)
            else:
                products=products
            

        else:
            products = products
        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(StoreProductList, self).get(request, store=store, products=products, filter_value=filter_value,
                                                 page=page,star_count=star_count,get_total_user_store_ratings=get_total_user_store_ratings,
                                                 get_average_rating_store=get_average_rating_store,
                                                 get_ratings=get_ratings,star_percentage=star_percentage,flavour_quick=flavour_quick,filter_by_flavour=filter_by_flavour,
                                                 occasion_quick=occasion_quick,filter_by_occasion=filter_by_occasion,tags_quick=tags_quick,filter_by_tags=filter_by_tags)

class SearchProduct(BaseView):
    template_name = 'client/cake-977/search.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)

        filter_by_flavour=request.GET.get('flavour_quick','')
        filter_by_occasion=request.GET.get('occasion_quick','')
        filter_by_tags=request.GET.get('tags_quick',None)
        if filter_by_tags== '':
            filter_by_tags=None

        keywords = request.GET.get('keywords', '')
        location = StoreLocation.get_store_location_obj(request)
        
        products = Product.objects.filter(Q(Q(name__icontains=keywords) |
                                              Q(category__name__icontains=keywords) |
                                              Q(store__name__icontains=keywords) |
                                              Q(store__location__name__icontains=keywords)) &
                                              Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location).prefetch_related(
                'tags').distinct()
        flavour_quick=Product.quickFlavour(products)
        occasion_quick=Product.quickOccasion(products)
        tags_quick=Product.quickTagsFilter(products)

        if filter_value == "price-hl":
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords)) &
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
            products=products.annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).order_by('-max_price','-max_price_2')
        
        elif filter_value == "price-lh":
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords)) &
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
            products=products.annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).order_by('max_price','max_price_2')

        elif filter_value == "rating":
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords)) & 
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location).annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).distinct().order_by('-product_review__review_star')
            products=products.annotate(product_review__review_star=Coalesce(Avg('product_review__review_star'),0)).order_by('-product_review__review_star')
        elif filter_by_flavour:
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords) |
            #                                   Q(store__name__icontains=keywords) |
            #                                   Q(store__location__name__icontains=keywords) |
            #                                   Q(brand__name__icontains=keywords)) &
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location,flavour__slug=filter_by_flavour).prefetch_related('tags').distinct()
            products=products.filter(flavour__slug=filter_by_flavour)
            if filter_by_tags and filter_by_occasion:
                products=products.filter(tags__name=filter_by_tags,category__slug=filter_by_occasion)
            elif filter_by_tags and not filter_by_occasion:
                products=products.filter(tags__name=filter_by_tags)
            elif not filter_by_tags and filter_by_occasion:
                products=products.filter(category__slug=filter_by_occasion)
            else:
                products=products
        elif filter_by_occasion:
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords) |
            #                                   Q(store__name__icontains=keywords) |
            #                                   Q(store__location__name__icontains=keywords) |
            #                                   Q(brand__name__icontains=keywords)) &
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location,category__slug=filter_by_occasion).prefetch_related('tags').distinct()
            products=products.filter(category__slug=filter_by_occasion)
            if filter_by_tags and filter_by_flavour:
                products=products.filter(tags__name=filter_by_tags,falvour__slug=filter_by_flavour)
            elif filter_by_tags and not filter_by_flavour:
                products=products.filter(tags__name=filter_by_tags)
            elif not filter_by_tags and filter_by_flavour:
                products=products.filter(flavour__slug=filter_by_flavour)
            else:
                products=products
        elif filter_by_tags:
            # products = Product.objects.filter(Q(Q(name__icontains=keywords) |
            #                                   Q(category__name__icontains=keywords) |
            #                                   Q(store__name__icontains=keywords) |
            #                                   Q(store__location__name__icontains=keywords) |
            #                                   Q(brand__name__icontains=keywords)) &
            #                                   Q(Q(store__is_active=True) & Q(is_available=True)),store__location=location,tags__name=filter_by_tags).prefetch_related('tags').distinct()
            products=products.filter(tags__name=filter_by_tags)
            if filter_by_occasion and filter_by_flavour:
                products=products.filter(category__slug=filter_by_occasion,falvour__slug=filter_by_flavour)
            elif filter_by_occasion and not filter_by_flavour:
                products=products.filter(category__slug=filter_by_occasion)
            elif not filter_by_occasion and filter_by_flavour:
                products=products.filter(flavour__slug=filter_by_flavour)
            else:
                products=products
        else:
            products = products
        paginator = Paginator(products, 40)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(SearchProduct, self).get(request, products_=products, keywords=keywords, filter_value=filter_value,
                                              page=page,flavour_quick=flavour_quick,filter_by_flavour=filter_by_flavour,
                                              occasion_quick=occasion_quick,filter_by_occasion=filter_by_occasion,tags_quick=tags_quick,filter_by_tags=filter_by_tags)


"""Profile page for client"""


class ClientProfile(LoginRequiredMixin, BaseView):
    login_url = reverse_lazy("accounts:login")
    template_name = 'client/user_profile_and_orders/profile.html'

    def get(self, request):
        form = ChangePasswordUserForm()
        return super(ClientProfile, self).get(request, form=form)


"""Profile page for client"""


class ClientOrders(LoginRequiredMixin, BaseView):
    login_url = reverse_lazy("accounts:login")
    template_name = 'client/user_profile_and_orders/orders.html'

    def get(self, request):
        settings = Settings.objects.all().get()
        orders = Order.objects.filter(customer=request.user).order_by('-id')
        search_keyword = request.GET.get('search_keyword', None)
        filter_keyword = request.GET.get('sort_order', None)
        if search_keyword:
            orders = Order.objects.filter(Q(customer=request.user) &
                                          (Q(order_number__icontains=search_keyword)))
        if filter_keyword == 'price':
            orders = Order.objects.filter(customer=request.user).order_by('-total')
        if filter_keyword == 'date':
            orders = Order.objects.filter(customer=request.user).order_by('-placed_on')

        # paginator = Paginator(orders, 5)
        # try:
        #    page = request.GET.get('page')
        #    order_pagination = paginator.get_page(page)
        # except PageNotAnInteger:
        #    order_pagination = paginator.get_page(1)
        # except EmptyPage:
        #    order_pagination = paginator.get_page(paginator.num_pages)
        return super(ClientOrders, self).get(request, orders=orders, settings=settings, search_keyword=search_keyword,
                                             filter_keyword=filter_keyword)



def cancelOrder(request):
    if request.method == 'POST':
        ids = request.POST.get('id', None)
        order = get_object_or_404(Order, id=ids)
        if order.order_status == 'Cancelled':
            return JsonResponse({'error': 'This order is already cancelled.'})
        Order.objects.filter(id=ids).update(order_status='Cancelled')
        order = get_object_or_404(Order, id=ids)
        return JsonResponse({'status': 'success', 'order_status': order.order_status})


class MobProfileNav(BaseView):
    template_name = 'client/user_profile_and_orders/mob_profile_nav.html'

    def get(self, request, *args, **kwargs):
        return super(MobProfileNav, self).get(request)

    

class ContactView(BaseView):
    template_name = 'client/cake-977/contactus.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return super(ContactView, self).get(request, form=form)

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been submitted.")
            return super(ContactView, self).get(request, success=True)
        return super(ContactView, self).get(request, form=form)


class TrackOrder(LoginRequiredMixin,BaseView):
    login_url = reverse_lazy("accounts:login")
    template_name = 'client/user_profile_and_orders/track_order.html'

    def get(self, request, *args, **kwargs):
        order_number = request.GET.get('order_number', None)
        order = False
        error = False
        delivery = []
        if order_number:
            try:
                if request.user.is_authenticated:
                    order = Order.objects.get(order_number=order_number, customer=request.user)
                else:
                    order = Order.objects.get(order_number=order_number)
                delivery = DeliveryNepxpress.objects.filter(order_number=order.order_number).order_by('id')
            except:

                error = 'Invalid order number.'
        return super(TrackOrder, self).get(request, order=order, error=error, delivery=delivery)


def subscribe(request):
    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'err': form.errors})


class ProductReviewView(LoginRequiredMixin,BaseView):
    login_url = reverse_lazy("accounts:login")
    template_name = 'client/cake-977/product_review.html'
    
    # @valid_product_location_only
    def get(self, request, *args, **kwargs):
        product=get_object_or_404(Product,id=self.kwargs['id'])
        allow_review_status=Product.allowReview(request,product)
        review_or_not=ProductReview.reviewed_or_not(request,product)
        return super(ProductReviewView, self).get(request,product=product,allow_review_status=allow_review_status,review_or_not=review_or_not)

    def post(self, request, *args, **kwargs):
        user=request.user
        product=get_object_or_404(Product,id=self.kwargs['id'])
        allow_review_status=Product.allowReview(request,product)
        if allow_review_status:
            point=request.POST.get('rating',None)
            comment=request.POST.get('comment',None)
            if ProductReview.objects.filter(customer=user,product=product).exists():
                review=ProductReview.objects.get(customer=user,product=product)
                ProductReview.update_product_review(user, product, review, point, comment,customer_purchased=False)
            else:
                ProductReview.create_product_review(comment, point, product, user, customer_purchased=False)
            messages.success(request, "You have successfully rated the product.")
        return redirect('client:product-detail',slug=product.slug)



class StoreReviewView(LoginRequiredMixin,BaseView):
    login_url = reverse_lazy("accounts:login")
    template_name = 'client/cake-977/store_review.html'
    
    @valid_store_location_only
    def get(self, request, *args, **kwargs):
        store=get_object_or_404(Store,id=self.kwargs['id'])
        return super(StoreReviewView, self).get(request,store=store)

    def post(self, request, *args, **kwargs):
        user=request.user
        store=get_object_or_404(Store,id=self.kwargs['id'])
        point=request.POST.get('rating',None)
        comment=request.POST.get('comment',None)
        if StoreReview.objects.filter(customer=user,store=store).exists():
            review=StoreReview.objects.get(customer=user,store=store)
            StoreReview.update_store_review(user, store, review, point, comment,customer_purchased=False)
        else:
            StoreReview.create_store_review(comment, point, store, user, customer_purchased=False)
        messages.success(request, "You have successfully rated the store.")
        return redirect('client:store-product-list',slug=store.slug)

class ProductReviewList(BaseView):
    template_name = 'client/cake-977/productReviewList.html'
    
    @valid_product_location_only
    def get(self, request, *args, **kwargs):
        filter_value=request.GET.get('filter_value',None)
        product=get_object_or_404(Product,slug=self.kwargs['slug'])
        if filter_value=='latest':
            reviews=ProductReview.objects.filter(product__slug=self.kwargs['slug']).order_by('-created_on')
        elif filter_value=='oldest':
            reviews=ProductReview.objects.filter(product__slug=self.kwargs['slug']).order_by('created_on')
        elif filter_value=='rating':
            reviews=ProductReview.objects.filter(product__slug=self.kwargs['slug']).order_by('-review_star')
        else:
            reviews=ProductReview.objects.filter(product__slug=self.kwargs['slug'])
        
        paginator = Paginator(reviews, 5)
        try:
           page = request.GET.get('page')
           order_pagination = paginator.get_page(page)
        except PageNotAnInteger:
           order_pagination = paginator.get_page(1)
        except EmptyPage:
           order_pagination = paginator.get_page(paginator.num_pages)



        return super(ProductReviewList, self).get(request,reviews=reviews,product=product,filter_value=filter_value)


class StoreReviewList(BaseView):
    template_name = 'client/cake-977/storeReviewList.html'
    
    @valid_store_location_only
    def get(self, request, *args, **kwargs):
        
        filter_value=request.GET.get('filter_value',None)
        store=get_object_or_404(Store,slug=self.kwargs['slug'])
        if filter_value=='latest':
            reviews=StoreReview.objects.filter(store__slug=self.kwargs['slug']).order_by('-created_on')
        elif filter_value=='oldest':
            reviews=StoreReview.objects.filter(store__slug=self.kwargs['slug']).order_by('created_on')
        elif filter_value=='rating':
            reviews=StoreReview.objects.filter(store__slug=self.kwargs['slug']).order_by('-review_star')
        else:
            reviews=StoreReview.objects.filter(store__slug=self.kwargs['slug'])
        
        paginator = Paginator(reviews, 5)
        try:
           page = request.GET.get('page')
           order_pagination = paginator.get_page(page)
        except PageNotAnInteger:
           order_pagination = paginator.get_page(1)
        except EmptyPage:
           order_pagination = paginator.get_page(paginator.num_pages)

        return super(StoreReviewList, self).get(request,reviews=reviews,store=store,filter_value=filter_value)

def cityAreaList(request):
    if request.method == 'GET':
        city=request.GET.get('city',None)
        city=get_object_or_404(Location,id=city)
        area=list(city.get_children().filter(is_active=True).values('id','name'))
        return JsonResponse({'status':'success','area':area})

def cityList(request):
    if request.method == 'GET':
        region=request.GET.get('region',None)
        region=get_object_or_404(Location,id=region)
        city=list(region.get_children().filter(is_active=True).values('id','name'))
        return JsonResponse({'status':'success','city':city})



from django.http import JsonResponse
from django.contrib.auth import get_user_model
User = get_user_model()

def autocomplete(request):
    if request.is_ajax():
        query = request.GET.get('keywords', '')
        product = list((Product.objects
                     .filter(Q(name__startswith=query)).distinct()
                     .values_list(('name'),flat=True)))
        if not query:
            product = []
        data = {
            'product': product,
        }
        return JsonResponse(data)



class AboutUs(BaseView):
    template_name='client/cake-977/about-us.html'
    def get(self, request, *args, **kwargs):
        return super(AboutUs, self).get(request,)

class TermsAndConditions(BaseView):
    template_name='client/cake-977/terms&condition.html'
    def get(self, request, *args, **kwargs):
        return super(TermsAndConditions, self).get(request,)

class PrivacyPolicy(BaseView):
    template_name='client/cake-977/privacypolicy.html'
    def get(self, request, *args, **kwargs):
        return super(PrivacyPolicy, self).get(request,)




# from django.shortcuts import render, redirect
# from django.http.response import Http404
# import requests
# import uuid
# import base64
# import json

# def send_order_sms(request):
#    url = "http://api.sparrowsms.com/v2/sms/"
#    headers= {
#          "Content-Type": "application/json"
#    }
#    payload = {
#       "token": "F6SQ2Mn444daU8Q8uDcU",
#       "from": 'deven',
#       "to": str(9862149135),
#       "text": 'testing'
#    }

#    response = requests.post(url, data = json.dumps(payload),headers= headers)
#    return response
   
   