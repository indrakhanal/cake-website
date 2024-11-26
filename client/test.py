from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from catalog.models import *
from settings.models import *
from sales.models import *
from .models import *
from datetime import date, datetime, timezone, timedelta
import datetime as dt
from django.db.models import Q
import secrets
from django.urls import reverse_lazy
from sales.models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from payment.models import *
from sales.sparrow import *
import json
import re
from django.db.models import Max, Min
from django.conf import settings as conf
from django.utils.decorators import method_decorator
from .models import MenuItem1
from django.views.decorators.csrf import csrf_exempt
from utility.hostname import *
import calendar
from django.contrib import messages
from accounts.forms import ChangePasswordUserForm
from utility.send_email import send_email_to_user
from django.core.validators import validate_email
from marketing.models import CartCoupon
from NewsletterandContact.forms import ContactForm, SubscriptionForm
from .utils import *
from store.models import Location as StoreLocation


def compareTime():
    my_date = date.today()
    day = calendar.day_name[my_date.weekday()]
    today_day = get_object_or_404(WeekDay, day=day)
    opening_time = today_day.opening_time
    closing_time = today_day.closing_time
    now = (datetime.now() + timedelta(hours=5.75)).time()
    if now >= opening_time and now < closing_time:
        return True
    else:
        return False


@method_decorator(csrf_exempt, name='dispatch')
class CatalogView(TemplateView):
    template_name = 'client/cake-977/index.html'

    def get_context_data(self, **kwargs):
        context = super(CatalogView, self).get_context_data(**kwargs)
        my_date = date.today()
        day = calendar.day_name[my_date.weekday()]
        coupon_code_req = self.request.GET.get('coupon', None)

        try:
            today_day = get_object_or_404(WeekDay, day=day)
            today_day = today_day.is_closed
            time_status = compareTime()
        except:
            today_day = False
            time_status = True
            sales_taxes = SalesTaxes.objects.all()
        try:
            settings = Settings.objects.all().get()
            currency = settings.currency
            minimum_order_price = settings.minimum_order_price

        except Settings.DoesNotExist:
            currency = "Rs"
            settings = ""
            minimum_order_price = 0
        context['store_locations'] = StoreLocation.objects.all()
        context['popular_flavour'] = Flavour.objects.filter(is_popular=True)
        context['subscriptionform'] = SubscriptionForm()
        context['best_seller'] = Product.objects.filter(is_best_seller=True, is_available=True).order_by(
            'display_order')[:8]
        context['recomended'] = Product.objects.filter(is_recomended=True, is_available=True)[:10]
        context['locations'] = Location.objects.all()
        context['minimum_order_price'] = minimum_order_price
        context['currency'] = currency
        context['today_day'] = today_day
        context['time_status'] = time_status
        context['coupon_code_req'] = coupon_code_req
        context['settings'] = settings
        context['category'] = Category.objects.filter(parent=None, is_available=True).order_by('display_order')
        context['cat_show_on_landing'] = Category.objects.filter(show_on_landing=True, is_available=True).order_by(
            'display_order')
        context['category'] = Category.objects.filter(parent=None, is_available=True)
        context['category_badge'] = Category.objects.filter(parent=None, is_available=True).order_by('display_order')[
                                    :7]
        context['active_store'] = Store.objects.filter(is_active=True)
        context['occasion'] = Occasion.objects.all()
        context['flavour'] = Flavour.objects.all()

        if not self.request.user.is_authenticated:
            try:
                if self.request.session.values():
                    data = sessionCalculation(self.request)
                    cart_list = data.get('cart_list')
                    sub_total = data.get('sub_total')
                    total = data.get('total')
                    cart_count = data.get('cart_count')
                    sales_taxes = data.get('sales_taxes')
                    total_with_taxes = data.get('total_with_taxes')
                    total_with_shipping_method = data.get('total_with_shipping_method')
                    shipping_cost_total = data.get('shipping_cost_total')

                    total1 = None
                    coupon = None

                    if 'coupon' in self.request.session:
                        coupon = self.request.session['coupon']
                        coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
                        if coupon.coupon_type == 'Flat':
                            total1 = total - coupon.value
                            total_with_taxes = SalesTaxes.sales_tax_total(total1)
                            total_with_shipping_method = total_with_taxes + shipping_cost_total
                        if coupon.coupon_type == 'Percentage':
                            total1 = total - (coupon.value / 100 * total)
                            total_with_taxes = SalesTaxes.sales_tax_total(total1)
                            total_with_shipping_method = total_with_taxes + shipping_cost_total

                    context['coupon'] = coupon
                    context['cart_list'] = cart_list
                    context['cart_count'] = cart_count
                    context['total'] = total
                    context['total1'] = total1
                    context['sub_total'] = sub_total
                    context['sales_taxes'] = sales_taxes
                    context['total_with_taxes'] = total_with_taxes
                    context['total_with_shipping_method'] = total_with_shipping_method
                    context['shipping_cost_total'] = shipping_cost_total
                return context

            except Exception as e:
                self.request.session.flush()
                total = 0
                total1 = None
                coupon = None
                context['coupon'] = None
                context['cart_list'] = None
                context['cart_count'] = 0
                context['total'] = 0
                context['total1'] = 0
                context['sales_taxes'] = 0
                return context

        if self.request.user.is_authenticated:

            try:
                Cart.objects.get(user=self.request.user)
            except:
                Cart.objects.create(user=self.request.user)
            cart = get_object_or_404(Cart, user=self.request.user)

            total = cart.total()
            sales_taxes = SalesTaxes.sales_tax_object(total)
            total_with_taxes = SalesTaxes.sales_tax_total(total)
            total_with_shipping_method = cart.get_total_with_shipping_method()

            total1 = None
            coupon = None
            if cart.coupon:
                total1 = cart.total_with_taxes_if_coupon(total).get('total1')
                total_with_taxes = cart.total_with_taxes_if_coupon(total).get('total_with_taxes')
                total_with_shipping_method = total_with_taxes + cart.get_shipping_price_total()
                coupon = get_object_or_404(CartCoupon, coupon_number=cart.coupon)

            context['cart_list'] = cart.cart_list
            context['coupon'] = coupon
            context['cart_count'] = cart.cart_count()
            context['total'] = total
            context['total1'] = total1
            context['sub_total'] = cart.get_sub_total()
            context['sales_taxes'] = sales_taxes
            context['total_with_taxes'] = total_with_taxes
            context['total_with_shipping_method'] = total_with_shipping_method
            context['shipping_cost_total'] = cart.get_shipping_price_total()
            return context

    def post(self, request):
        my_date = date.today()
        day = calendar.day_name[my_date.weekday()]
        try:
            today_day = get_object_or_404(WeekDay, day=day)
            today_day = today_day.is_closed
            time_status = compareTime()
        except:
            today_day = False
            time_status = True

        updateCouponInCartOrSession(self.request)

        try:
            settings = Settings.objects.all().get()
            minimum_order_price = settings.minimum_order_price
        except Settings.DoesNotExist:
            settings = ""
            minimum_order_price = 0

        product = int(request.POST.get('product', None))
        product_varient = request.POST.get('varient', None)
        quantity = request.POST.get('quantity', None)
        if not quantity:
            quantity = 1
        addons = request.POST.getlist('addons', None)
        addons_quantity = request.POST.getlist('addons_quantity', None)

        while ("" in addons_quantity):
            addons_quantity.remove("")
            addons.remove("")

        date_delivery = request.POST.get('delivery_date', None)

        time = '1'  # request.POST.get('time',None)
        message = request.POST.get('message', None)
        is_buy = request.POST.get('is_buy', None)

        is_eggless = request.POST.get('is_eggless', None)
        is_sugarless = request.POST.get('is_sugarless', None)
        flavour = request.POST.get('flavour', None)
        pound = request.POST.get('pound', None)
        shipping_method = 6  # request.POST.get('shipping_method',None)

        product_ = get_object_or_404(Product, id=product)
        varient_ = get_object_or_404(ProductVarient, id=product_varient)

        # if settings.is_conditional_delivery_charge:
        #    conditional_charge=conditionalDeliveryCharge(request)
        # else:
        #    conditional_charge=0

        if not varient_.quantity < 1 and not varient_.quantity < int(quantity) and int(quantity) >= 1:
            if not self.request.user.is_authenticated:
                menu = []
                menu.append(
                    MenuItem1(product, varient_.id, quantity, addons, addons_quantity, date_delivery, time, message,
                              pound, is_eggless, is_sugarless, shipping_method, flavour).serialize())
                key = str(product) + str(varient_.id) + str(date_delivery) + str(time)

                if str(key) in request.session:
                    old_quantity = str(request.session[str(key)][0]['quantity'])
                    new_quantity = int(quantity) + int(old_quantity)
                    if new_quantity > varient_.quantity:
                        return JsonResponse({'error': 'Selected quantity isnot available on stock'})

                    del request.session[str(key)]
                    menu1 = []
                    menu1.append(
                        MenuItem1(product, varient_.id, new_quantity, addons, addons_quantity, date_delivery, time,
                                  message, pound, is_eggless, is_sugarless, shipping_method, flavour).serialize())
                    request.session[str(key)] = menu1
                else:
                    request.session[str(key)] = menu

                if is_buy == 'yes':
                    return JsonResponse({'status': 'Success', 'is_buy': 'yes'})
                else:
                    return JsonResponse({'status': 'Success'})

            if self.request.user.is_authenticated:
                if flavour:
                    flavour = get_object_or_404(Flavour, id=flavour)
                cart = Cart.objects.get(user=self.request.user)
                shipping_method = get_object_or_404(ShippingMethod, id=shipping_method)
                varient = get_object_or_404(ProductVarient, id=product_varient)
                CartItem.addToCart(cart, varient_, date_delivery, time, is_eggless, is_sugarless, message,
                                   shipping_method, pound, quantity, addons, addons_quantity, flavour)
                if is_buy == 'yes':
                    return JsonResponse({'status': 'Success', 'is_buy': 'yes'})
                else:
                    return JsonResponse({'status': 'Success'})

        else:
            return JsonResponse({'error': 'Selected quantity is not available on stock'})


class CheckoutCartView(CatalogView):
    template_name = 'client/cake-977/cart.html'

    def get(self, request, *args):
        return super(CheckoutCartView, self).get(request)


class ProductDetailView(CatalogView):
    template_name = 'client/cake-977/product_detail.html'

    def get(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        tags = product.tags
        images = product.images

        related_product = product.related_products.all()[:4]

        try:
            value = product.first_varient_attributes()
            print(value, "----**")
            if value:
                value = value['value'][0]
                varients = ProductVarient.objects.filter(product=product, attribut_value__value=value)
                print(varients, "=====")
                related_values = []
                for item in varients:
                    for item2 in item.attribut_value.all():
                        if not item2.value == value:
                            related_values.append(item2.value)
                print(related_values)
                if related_values:
                    first_varient_id = \
                        ProductVarient.objects.filter(product=product, attribut_value__value=value).filter(
                            product=product,
                            attribut_value__value=
                            related_values[
                                0])[0].id
                    first_varient = ProductVarient.objects.filter(product=product, attribut_value__value=value).filter(
                        product=product, attribut_value__value=related_values[0])
                else:
                    first_varient_id = ProductVarient.objects.filter(product=product, attribut_value__value=value)[0].id
                    first_varient = ProductVarient.objects.filter(product=product, attribut_value__value=value)

                return super(ProductDetailView, self).get(request, product=product, related_product=related_product,
                                                          images=images, related_values=related_values,
                                                          first_varient_id=first_varient_id,
                                                          first_varient=first_varient)
            else:
                return super(ProductDetailView, self).get(request, product=product, related_product=related_product,
                                                          images=images, first_varient_id=product.product.all()[0].id,
                                                          first_varient=product.product.all())

        except Exception as e:
            print(e, "+++++==")
            return super(ProductDetailView, self).get(request, product=product, related_product=related_product,
                                                      images=images, first_varient_id=product.product.all()[0].id,
                                                      first_varient=product.product.all())

    def post(self, request, *args, **kwargs):
        from django.db.models import Q
        product = get_object_or_404(Product, slug=kwargs['slug'])
        value = self.request.POST.get('value1', None)
        first_attr = self.request.POST.get('first_attr', None)
        second_attr = self.request.POST.get('second_attr', None)
        if value:
            varients = ProductVarient.objects.filter(product=product, attribut_value__value=value)
            related_values = []
            for item in varients:
                for item2 in item.attribut_value.all():
                    if not item2.value == value:
                        related_values.append(item2.value)
            print(related_values, "--------")
            if related_values:
                first_varient_id = \
                    ProductVarient.objects.filter(product=product, attribut_value__value=value).filter(product=product,
                                                                                                       attribut_value__value=
                                                                                                       related_values[
                                                                                                           0])[
                        0].id
                return JsonResponse({'available_values': related_values, 'first_varient_id': first_varient_id})
            else:
                first_varient_id = ProductVarient.objects.filter(product=product, attribut_value__value=value)[0]
                print(first_varient_id, "&&&&&")
                return JsonResponse({'first_varient_id': first_varient_id.id, 'old_price': first_varient_id.old_price,
                                     'new_price': first_varient_id.selling_price})

        if first_attr and second_attr:
            varient_id = ProductVarient.objects.filter(product=product, attribut_value__value=first_attr).filter(
                product=product, attribut_value__value=second_attr)
            return JsonResponse({'varient_id': varient_id[0].id, 'old_price': varient_id[0].old_price,
                                 'new_price': varient_id[0].selling_price})


def cartQuantityUpdate(request):
    if request.method == 'POST':
        updateCouponInCartOrSession(request)
        product_varient = request.POST.get('varient', None)
        quantity = request.POST.get('quantity', None)
        delivery_date = request.POST.get('delivery_date', None)
        time = request.POST.get('time', None)
        product = ProductVarient.objects.get(id=product_varient).product.id
        if not request.user.is_authenticated:
            key = str(product) + str(product_varient) + str(delivery_date) + str(time)
            session_quantity = request.session[str(key)][0].get('quantity')
            if int(quantity) <= 0:
                del request.session[str(key)]
            else:
                if ProductVarient.objects.get(id=product_varient).quantity < int(quantity):
                    return JsonResponse({'error': 'Quantity unavailable.'})
                else:
                    request.session[str(key)][0].update(quantity=quantity)
            return JsonResponse({'status': 'Success'})

        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            if int(quantity) >= 1:
                CartItem.objects.filter(cart=cart, product=product_varient, date=delivery_date, time=time).update(
                    quantity=quantity)
            else:
                try:
                    CartItem.objects.get(cart=cart, product=product_varient, date=delivery_date, time=time).delete()
                except:
                    return JsonResponse({'error': 'Item doesnot exist.'})
            return JsonResponse({'status': 'Success'})


def applyCoupon(request):
    if request.method == "POST":
        my_date = date.today()
        day = calendar.day_name[my_date.weekday()]
        try:
            today_day = get_object_or_404(WeekDay, day=day)
            today_day = today_day.is_closed
            time_status = compareTime()
        except:
            today_day = False
            time_status = True
        try:
            settings = Settings.objects.all().get()
            minimum_order_price = settings.minimum_order_price
        except Settings.DoesNotExist:
            settings = ""
            minimum_order_price = 0
        coupon_number = str(request.POST.get('coupon', None))

        if not request.user.is_authenticated:
            sub_total = 0
            cart_count = 0
            addons_price_grand_total = 0
            if request.session.values():
                for key, item in request.session.items():
                    if not (
                            key == "_auth_user_id" or key == "_auth_user_backend" or key == "_auth_user_hash" or key == "_password_reset_key" or key == "coupon"):
                        varient_product = item[0].get('product_varient')
                        quantity = item[0].get('quantity')
                        cart_count = cart_count + int(quantity)
                        sub_total = sub_total + (
                                ProductVarient.objects.filter(id=varient_product)[0].selling_price * int(quantity))

                        addons = item[0].get('addons')
                        addons_quantity = item[0].get('addons_quantity')
                        addons_price_total = productAddontotal(addons, addons_quantity)
                        addons_price_grand_total = addons_price_grand_total + addons_price_total.get(
                            'addons_price_total')
                total = sub_total + addons_price_grand_total
                # previous_total = total
            else:
                return JsonResponse({'error': 'No item in your cart.', 'coupon': coupon_number})
        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            cart_count = cart.cart_count()
            if cart.cart_count() >= 1:
                total = cart.get_sub_total()
                # previous_total=total

            else:
                return JsonResponse({'error': 'No item in your cart.', 'coupon': coupon_number})

        try:
            coupon = CartCoupon.objects.get(coupon_number=coupon_number, is_active=True)
            current_time = datetime.now(timezone.utc).date()
            coupon_per_user_limit = coupon.per_user_limit
            coupon_limit = coupon.total_user_limit
            min_cart_amount = coupon.min_cart_price
            max_cart_amount = coupon.max_cart_price
            time_limit = coupon.time_limit

            # user_coupon_count=Order.objects.filter(~Q(order_status='Cancelled'),customer=request.user,coupon=coupon).count()
            coupon_total_used = Order.objects.filter(~Q(order_status='Cancelled'), coupon=coupon).count()

            check_time_validity = current_time < time_limit
            check_price_range_validity = min_cart_amount <= total <= max_cart_amount
            # check_user_per_limit_validity=user_coupon_count<coupon_per_user_limit
            check_total_coupon_limit_validity = coupon_total_used < coupon_limit
            if check_time_validity and check_price_range_validity and check_total_coupon_limit_validity:
                if not request.user.is_authenticated:
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
                    Cart.objects.filter(user=request.user).update(coupon=coupon_number)
                    cart = get_object_or_404(Cart, user=request.user)
                    if cart.coupon:
                        coupon = get_object_or_404(CartCoupon, coupon_number=cart.coupon)
                        previous_total = total
                        if coupon.coupon_type == 'Flat':
                            total = total - coupon.value
                        if coupon.coupon_type == 'Percentage':
                            total = total - (coupon.value / 100 * total)

                sales_taxes_ob = SalesTaxes.sales_tax_object(total)
                total_with_taxes = SalesTaxes.sales_tax_total(total)
                # if settings.is_conditional_delivery_charge:
                #    conditional_charge=conditionalDeliveryCharge(request)
                # else:
                #    conditional_charge=0

                return JsonResponse({'status': 'Success', 'coupon': model_to_dict(coupon), 'total': total,
                                     'previous_total': previous_total, 'sales_taxes': sales_taxes_ob,
                                     'total_with_taxes': total_with_taxes, 'minimum_order_price': minimum_order_price,
                                     'cart_count': cart_count, 'time_status': time_status, 'today_day': today_day})

            else:
                return JsonResponse(
                    {'error': 'Cart requirement unfulfilled.', 'coupon': coupon_number, 'min_value': min_cart_amount,
                     'max_value': max_cart_amount, 'validity_date': coupon.time_limit})

        except:
            return JsonResponse({'error': 'Invalid Coupon.', 'coupon': coupon_number})


def placeOrder(request):
    if request.method == 'POST':
        i_am_receiver = request.POST.get('i_am_receiver', False)
        receiver_fullname = request.POST.get('receiver_fullname', None)
        receiver_email = request.POST.get('receiver_email', None)
        receiver_address = request.POST.get('receiver_address', None)
        landmark = request.POST.get('landmark', None)
        address_type = request.POST.get('address_type', None)
        receiver_number1 = request.POST.get('receiver_number1', None)
        receiver_number2 = request.POST.get('receiver_number2', None)
        occasion = request.POST.get('occasion', None)
        sender_full_name = request.POST.get('sender_full_name', None)
        sender_phone_number = request.POST.get('sender_phone_number', None)
        sender_email = request.POST.get('sender_email', None)
        hide_info_from_receiver = request.POST.get('hide_info_from_receiver', False)
        payment_method = request.POST.get('payment_method', None)

        i_am_receiver = True if i_am_receiver else False
        hide_info_from_receiver = True if hide_info_from_receiver else False
        response = validate_order_request(receiver_fullname, receiver_address, receiver_number1, sender_full_name,
                                          sender_phone_number, receiver_email, sender_email, payment_method)

        if response:
            return JsonResponse({'error': response})

        my_date = date.today()
        day = calendar.day_name[my_date.weekday()]
        try:
            today_day = get_object_or_404(WeekDay, day=day)
            today_day = today_day.is_closed
            time_status = compareTime()
        except:
            today_day = False
            time_status = True

        if not time_status or today_day:
            return JsonResponse({'error': 'Store is closed now.'})

        settings_object = Settings.objects.all().get()
        user = get_user_model()

        if not request.user.is_authenticated:
            user_obj = None
            data = sessionCalculation(request)
            total = data.get('total')
            cart_count = data.get('cart_count')

        if request.user.is_authenticated:
            user_obj = request.user
            cart = get_object_or_404(Cart, user=request.user)
            cart_count = cart.cart_count()
            total = cart.get_sub_total()

        if float(total) < float(settings_object.minimum_order_price):
            return JsonResponse(
                {'error': 'Minimum cart requirement is a subtotal of ' + str(settings_object.minimum_order_price)})

        if cart_count <= 0:
            return JsonResponse({'error': 'You do not have item in cart.'})

        address = DeliveryAddress.createDeliveryAddress(i_am_receiver, receiver_fullname,
                                                        receiver_email, receiver_address, landmark, address_type,
                                                        receiver_number1,
                                                        receiver_number2, occasion, sender_full_name,
                                                        sender_phone_number, sender_email, hide_info_from_receiver)

        if address:
            if not request.user.is_authenticated:
                data = sessionCalculation(request)
                total = data.get('total')
                sale_obj = data.get('sales_taxes')
                tax_rate = []
                for item in sale_obj:
                    total = total + float(item.get('value'))
                    tax_rate.append(item)

                order_number = secrets.token_hex(3)
                if Order.objects.filter(order_number=order_number).exists():
                    order_number = order_number + secrets.token_hex(1)

                if 'coupon' in request.session:
                    coupon = request.session['coupon']
                    coupon = get_object_or_404(CartCoupon, coupon_number=coupon)
                    if coupon.coupon_type == 'Flat':
                        discount = coupon.value
                    if coupon.coupon_type == 'Percentage':
                        discount = (coupon.value / 100) * total
                else:
                    coupon = discount = None

                order = Order.objects.create(customer=user_obj,
                                             order_number=order_number,
                                             discount=discount,
                                             coupon=coupon,
                                             sub_total_order=total,
                                             refunded_amount=0,
                                             shipping_cost=data.get('shipping_cost_total'),
                                             delivery_address=address,
                                             delivery_date=None,
                                             total=data.get('total_with_shipping_method'),
                                             tax_rate=tax_rate,
                                             order_from='Direct',
                                             order_status='Unconfirmed',
                                             payment_status='Awaiting Payment',
                                             customer_notes=None,
                                             )

                for item in sale_obj:
                    OrderExtraCharge.objects.create(order=order, name=item['name'], rate=item['rate'],
                                                    total=item['value'])

                for item in data.get('cart_list'):
                    varient = item.get('varient')
                    addons = item.get('addons')
                    addons_quantity = item.get('addons_quantity')
                    flavour = get_object_or_404(Flavour, id=item.get('flavour'))
                    is_eggless = item.get('is_sugarless')
                    is_sugarless = item.get('is_sugarless')

                    if is_sugarless:
                        is_sugarless = True
                    else:
                        is_sugarless = False

                    if is_eggless:
                        is_eggless = True
                    else:
                        is_eggless = True

                    order_item = OrderItem.objects.create(order=order,
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
                                                          flavour=flavour,
                                                          pound=item.get('pound'),
                                                          )

                    if addons and len(addons) >= 1:
                        a = 0
                        for i in addons:
                            addon = get_object_or_404(ProductAddons, id=i)
                            AddonOrderItem.objects.create(order_item=order_item, addons=addon,
                                                          quantity=addons_quantity[a])
                            a = a + 1

                    quantity = varient[0].quantity - 1
                    ProductVarient.objects.filter(id=varient[0].id).update(quantity=quantity)
                CustomerDetail.create_customer_detail(order_number)

                request.session.flush()
                return JsonResponse({'status': 'Success', 'reference': order_number})

            if request.user.is_authenticated:
                cart = get_object_or_404(Cart, user=request.user)
                sub_total_sales = cart.get_sub_total()
                total = cart.get_total_with_shipping_method()

                sale_obj = SalesTaxes.sales_tax_object(sub_total_sales)
                tax_rate = []
                for item in sale_obj:
                    total = total + float(item.get('value'))
                    tax_rate.append(item)

                order_number = secrets.token_hex(3)
                if Order.objects.filter(order_number=order_number).exists():
                    order_number = order_number + secrets.token_hex(1)

                discount = cart.discount.get('discount')
                coupon = cart.discount.get('coupon')

                order = Order.objects.create(customer=user_obj,
                                             order_number=order_number,
                                             discount=discount,
                                             coupon=coupon,
                                             sub_total_order=sub_total_sales,
                                             refunded_amount=0,
                                             shipping_cost=cart.get_shipping_price_total(),
                                             delivery_address=address,
                                             delivery_date=None,
                                             total=total,
                                             tax_rate=tax_rate,
                                             order_from='Direct',
                                             order_status='Unconfirmed',
                                             payment_status='Awaiting Payment',
                                             customer_notes=None,
                                             )

                for item in sale_obj:
                    OrderExtraCharge.objects.create(order=order, name=item['name'], rate=item['rate'],
                                                    total=item['value'])

                for item in CartItem.objects.filter(cart=cart):

                    order_item = OrderItem.objects.create(order=order,
                                                          product=item.product,
                                                          price=item.product.selling_price,
                                                          quantity=item.quantity,
                                                          sub_total=item.get_sub_total(),
                                                          total=item.get_total_with_shipping_cost(),
                                                          special_instruction=item.message,
                                                          is_sugerless=item.is_sugarless,
                                                          is_eggless=item.is_eggless,
                                                          date=item.date,
                                                          time=item.time,
                                                          shipping_method=item.shipping_method,
                                                          flavour=item.flavour,
                                                          pound=item.pound
                                                          )
                    item_order = get_object_or_404(OrderItem, id=order_item.id)
                    if item.item_addons:
                        for i in item.item_addons.all():
                            AddonOrderItem.objects.create(order_item=item_order,
                                                          addons=i.addons,
                                                          quantity=i.quantity
                                                          )

                    quantity = ProductVarient.objects.get(id=item.product.id).quantity - 1
                    ProductVarient.objects.filter(id=item.product.id).update(quantity=quantity)

                CustomerDetail.create_customer_detail(order_number)

                CartItem.objects.filter(cart=cart).delete()

            return JsonResponse(
                {'status': 'Success', 'reference': order_number})


        else:
            JsonResponse({'error': 'Enter your address.'})


class OrderSuccess(CatalogView):
    template_name = 'client/cake-977/order_success.html'

    def get(self, request, *args, **kwargs):
        order_number = self.kwargs['order_number']
        order = get_object_or_404(Order, order_number=order_number)
        return super(OrderSuccess, self).get(request, order=order)


class StoreList(CatalogView):
    template_name = 'client/cake-977/shop_wise_list.html'

    def get(self, request, *args, **kwargs):
        stores = Store.objects.filter(is_active=True)
        return super(StoreList, self).get(request, stores=stores)


def send_email_ajax(request):
    settings_object = Settings.objects.all().get()
    contact_number = settings_object.contact_number
    order_number = request.GET.get('order_number', None)
    order = Order.objects.get(order_number=str(order_number))
    baseurl = hostname_from_request(request)

    if conf.LIVE:
        # Sparrow SMS
        try:
            vendor_number = str(contact_number)[-10:]
            message = "You have received new order from " + str(order.delivery_address.full_name)[
                                                            -15:] + ". Order ID: " + str(
                order.order_number) + ".Total Amt: " + str(
                order.total) + ".For details please check your Ordersathi Dashboard."
            send_order_sms("InfoSMS", vendor_number, str(message)[:155])
            pass

        except Exception as e:
            pass

    # Email
    try:
        extra_charges = OrderExtraCharge.objects.filter(order=order)
    except:
        extra_charges = []
    setting_ = Settings.objects.all().get()
    currency = setting_.currency

    send_email_to_user(subject_name="Thank you for your order", to_email=str(order.delivery_address.email),
                       obj={'order': order, 'setting': setting_, 'extra_charges': extra_charges, 'currency': currency,
                            'base_url': baseurl}, template_location="email_templates/order_placed.html")
    return JsonResponse({})


class CategoryProduct(CatalogView):
    template_name = 'client/cake-977/list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)

        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        cat_descendants = category.get_descendants(include_self=True).filter(is_available=True)
        cat_all_children = category.get_descendants(include_self=False).filter(is_available=True)

        if filter_value == "price-hl":
            products = Product.objects.filter(store__is_active=True, is_available=True,
                                              category__in=cat_descendants).prefetch_related(
                'tags').distinct().order_by('-product__old_price')
        if filter_value == "price-lh":
            products = Product.objects.filter(store__is_active=True, is_available=True,
                                              category__in=cat_descendants).prefetch_related(
                'tags').distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(store__is_active=True, is_available=True,
                                              category__in=cat_descendants).prefetch_related('tags').distinct()

        paginator = Paginator(products, 2)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)
        return super(CategoryProduct, self).get(request, products_=products, slug=self.kwargs['slug'],
                                                category_=category, cat_all_children=cat_all_children,
                                                filter_value=filter_value, page=page)


class LocationProduct(CatalogView):
    template_name = 'client/cake-977/location_list.html'

    def get(self, request, *args, **kwargs):

        location_slug = request.GET.get('store_locations', None)

        filter_value = request.GET.get('filter', None)
        location = get_object_or_404(StoreLocation, slug=location_slug)

        if filter_value == "price-hl":
            products = Product.objects.filter(Q(store__location__slug=location_slug) & Q(store__is_active=True) & Q(
                is_available=True)).distinct().order_by('-product__old_price')

        if filter_value == "price-lh":

            products = Product.objects.filter(Q(store__location__slug=location_slug) & Q(store__is_active=True) & Q(
                is_available=True)).distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(store__location__slug=location_slug, store__is_active=True,
                                              is_available=True).distinct()

        paginator = Paginator(products, 20)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(LocationProduct, self).get(request, location=location, products=products,
                                                filter_value=filter_value, location_slug=location_slug, page=page)


class PriceRangeList(CatalogView):
    template_name = 'client/cake-977/price_range_list.html'

    def get(self, request, *args, **kwargs):

        min_price = request.GET.get('min_price', None)
        max_price = request.GET.get('max_price', None)

        filter_value = request.GET.get('filter', None)
        if filter_value == "price-hl" and min_price and max_price:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True)).distinct().order_by('-product__old_price')

        if filter_value == "price-lh" and min_price and max_price:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True)).distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(
                Q(product__old_price__range=(min_price, max_price)) & Q(store__is_active=True) & Q(
                    is_available=True)).distinct()

        paginator = Paginator(products, 2)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(PriceRangeList, self).get(request, products=products, filter_value=filter_value, page=page,
                                               min_price=min_price, max_price=max_price)


class FlavourProductList(CatalogView):
    template_name = 'client/cake-977/flavour_product_list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)
        flavour = get_object_or_404(Flavour, id=self.kwargs['pk'])

        if filter_value == "price-hl":
            products = Product.objects.filter(
                Q(flavour__id=self.kwargs['pk']) & Q(is_available=True) & Q(store__is_active=True)).distinct().order_by(
                '-product__old_price')
        elif filter_value == "price-lh":
            products = Product.objects.filter(
                Q(flavour__id=self.kwargs['pk']) & Q(is_available=True) & Q(store__is_active=True)).distinct().order_by(
                'product__old_price')
        else:
            products = Product.objects.filter(
                Q(flavour__id=self.kwargs['pk']) & Q(is_available=True) & Q(store__is_active=True)).distinct()

        paginator = Paginator(products, 2)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(FlavourProductList, self).get(request, flavour_=flavour, products=products,
                                                   filter_value=filter_value, page=page)


class OccasionProductList(CatalogView):
    template_name = 'client/cake-977/occasion_product_list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)
        occasion = get_object_or_404(Occasion, id=self.kwargs['pk'])

        if filter_value == "price-hl":
            products = Product.objects.filter(Q(occasion__id=self.kwargs['pk']) & Q(is_available=True) & Q(
                store__is_active=True)).distinct().order_by('-product__old_price')
        elif filter_value == "price-lh":
            products = Product.objects.filter(Q(occasion__id=self.kwargs['pk']) & Q(is_available=True) & Q(
                store__is_active=True)).distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(
                Q(occasion__id=self.kwargs['pk']) & Q(is_available=True) & Q(store__is_active=True)).distinct()

        paginator = Paginator(products, 2)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(OccasionProductList, self).get(request, occasion_=occasion, products=products,
                                                    filter_value=filter_value, page=page)


class StoreProductList(CatalogView):
    template_name = 'client/cake-977/store_product_list.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)
        store = get_object_or_404(Store, slug=self.kwargs['slug'])
        if filter_value == "price-hl":
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True)).distinct().order_by('-product__old_price')
        elif filter_value == "price-lh":
            products = Product.objects.filter(Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(
                store__is_active=True)).distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(
                Q(store__slug=self.kwargs['slug']) & Q(is_available=True) & Q(store__is_active=True)).distinct()

        paginator = Paginator(products, 20)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(StoreProductList, self).get(request, store=store, products=products, filter_value=filter_value,
                                                 page=page)


class SearchProduct(CatalogView):
    template_name = 'client/cake-977/search.html'

    def get(self, request, *args, **kwargs):

        filter_value = request.GET.get('filter', None)

        keywords = request.GET.get('keywords', None)

        if filter_value == "price-hl" and keywords:
            products = Product.objects.filter(Q(name__icontains=keywords) |
                                              Q(category__name__icontains=keywords) |
                                              Q(store__name__icontains=keywords) |
                                              Q(store__location__name__icontains=keywords) |
                                              Q(brand__name__icontains=keywords) & Q(
                Q(store__is_active=True) & Q(is_available=True))).distinct().order_by('-product__old_price')
        if filter_value == "price-lh" and keywords:
            products = Product.objects.filter(Q(name__icontains=keywords) |
                                              Q(category__name__icontains=keywords) |
                                              Q(store__name__icontains=keywords) |
                                              Q(store__location__name__icontains=keywords) |
                                              Q(brand__name__icontains=keywords) & Q(
                Q(store__is_active=True) & Q(is_available=True))).distinct().order_by('product__old_price')
        else:
            products = Product.objects.filter(Q(name__icontains=keywords) |
                                              Q(category__name__icontains=keywords) |
                                              Q(store__name__icontains=keywords) |
                                              Q(store__location__name__icontains=keywords) |
                                              Q(brand__name__icontains=keywords) &
                                              Q(Q(store__is_active=True) & Q(is_available=True))).prefetch_related(
                'tags').distinct()

        paginator = Paginator(products, 2)
        try:
            page = request.GET.get('page')
            products = paginator.get_page(page)
        except PageNotAnInteger:
            products = paginator.get_page(1)
        except EmptyPage:
            products = paginator.get_page(paginator.num_pages)

        return super(SearchProduct, self).get(request, products_=products, keywords=keywords, filter_value=filter_value,
                                              page=page)


"""Profile page for client"""


class ClientProfile(LoginRequiredMixin, CatalogView):
    login_url = reverse_lazy("accounts:login1")
    template_name = 'client/user_profile_and_orders/profile.html'

    def get(self, request):
        form = ChangePasswordUserForm()
        return super(ClientProfile, self).get(request, form=form)


"""Profile page for client"""


class ClientOrders(LoginRequiredMixin, CatalogView):
    login_url = reverse_lazy("accounts:login1")
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


@login_required
def cancelOrder(request):
    if request.method == 'POST':

        ids = request.POST.get('id', None)
        order = get_object_or_404(Order, id=ids)
        if order.order_status == 'Cancelled':
            return JsonResponse({'error': 'This order is already cancelled.'})
        Order.objects.filter(id=ids).update(order_status='Cancelled')
        order = get_object_or_404(Order, id=ids)
        return JsonResponse({'status': 'success', 'order_status': order.order_status})


class ContactView(CatalogView):
    template_name = 'client/store/contact.html'

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


class TrackOrder(LoginRequiredMixin, CatalogView):
    login_url = reverse_lazy("accounts:login1")
    template_name = 'client/user_profile_and_orders/track_order.html'

    def get(self, request, *args, **kwargs):
        order_number = request.GET.get('order_number', None)
        order = False
        error = False
        delivery = []
        if order_number:
            try:
                order = Order.objects.get(order_number=order_number, customer=request.user)
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
