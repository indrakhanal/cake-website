from django import template
from settings.models import Settings
from sales.models import Order,OrderItem
from store.models import Location as StoreLocation
from catalog.models import Product,Store
register = template.Library()


@register.filter
def outlet_name(user):
    try:
        settings = Settings.objects.all()
        outlet_name = settings[0].outlet_name
        return outlet_name
    except:
        outlet_name = ""
        return outlet_name


@register.filter
def unconfirmed_order(user):
    count = Order.objects.filter(order_status="Unconfirmed").count()
    return count

@register.filter
def unconfirmed_order_item(user):
    count = OrderItem.objects.filter(order_status="Unconfirmed").count()
    return count


@register.filter
def currency_symbol(user):
    try:
        settings = Settings.objects.values('currency')
        return settings.currency
    except:
        return "Rs"

@register.filter
def get_top_text(user):
    try:
        settings = Settings.objects.all()
        banner_top_message = settings[0].banner_top_message
        return banner_top_message
    except:
        return ""

@register.filter
def get_top_url(user):
    try:
        settings = Settings.objects.all()
        banner_top_message_url = settings[0].banner_top_message_redirect
        return banner_top_message_url
    except:
        return ""

@register.filter
def get_current_location_name(request):
    if 'location_id' in request.session:
        return StoreLocation.objects.get(id=int(request.session['location_id']))
    else:
        return StoreLocation.objects.first()

@register.filter
def get_current_location_slug(request):
    if 'location_id' in request.session:
        try:
            return StoreLocation.objects.get(id=int(request.session['location_id'])).slug
        except:
            return None
    else:
        try:
            return StoreLocation.objects.first().slug
        except:
            return None

@register.filter
def location_pop_up_show(request):
    if 'location_id' in request.session:
        return False
    return True

@register.filter
def product_detail_popup(request,product):
    print(request.session.get('location_id'),"Session value")
    if 'location_id' in request.session:
        if (Store.objects.filter(location__id__in=[request.session['location_id']],store_product=product).exists()):
            print("1")
            return False
        else:
            print("2")
            return True
    return True
@register.filter
def product_detail_popup(request,product):
    print(request.session.get('location_id'),"Session value")
    if 'location_id' in request.session:
        if (Store.objects.filter(location__id__in=[request.session['location_id']],store_product=product).exists()):
            return False
        else:
            return True
    return True

@register.filter
def product_available_location(product):
    store = Store.objects.filter(store_product=product).prefetch_related('location')
    locations = []
    for item in store:
        for location in item.location.all():
            locations.append({'location':location.name})
    return locations

