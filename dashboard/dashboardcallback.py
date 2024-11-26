from sales.models import Order, OrderItem,DeliveryAddress
from catalog.models import Product,ProductVarient
from django.db.models import Count
from django.db.models import Sum

'''Recent Orders'''


def most_recent_orders():
    
    return Order.objects.order_by('-id')[:10]


'''Customers Analytics'''

def first_time_customers(Customer):
    
    mobile_number = Order.objects.order_by('-delivery_address__contact_number').values('delivery_address__contact_number').distinct()[:10]
    # mobile_number = DeliveryAddress.objects.order_by('-contact_number').values('contact_number').distinct()
    new_customer_order_list = []
    for item in mobile_number:
        total_orders = Order.objects.filter(delivery_address__contact_number =item['delivery_address__contact_number']).count()
        total_value = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).aggregate(total_price=Sum('total'))['total_price']
        name_list = DeliveryAddress.objects.values('sender_fullname').filter(contact_number=item['delivery_address__contact_number'])
        if total_value:
            total_value = total_value
        else:
            total_value = 0
        
        new_customer_order_list.append({
            'name': name_list[0]['sender_fullname'],
            'mobile': item['delivery_address__contact_number'],
            'id':"1",
            'orders': total_orders,
            'total_value': total_value
        })
    return new_customer_order_list
    
  

from django.db.models import Count
def most_orders_customers(Customer):

    mobile_number = Order.objects.order_by('delivery_address__contact_number').values('delivery_address__contact_number').distinct()[:10]
    
    new_customer_order_list = []
    for item in mobile_number:
        total_orders = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).count()
        total_value = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).aggregate(total_price=Sum('total'))['total_price']
        name_list = DeliveryAddress.objects.values('sender_fullname').filter(contact_number=item['delivery_address__contact_number'])
        if total_value:
            total_value = total_value
        else:
            total_value = 0
        
        new_customer_order_list.append({
            'name': name_list[0]['sender_fullname'],
            'mobile': item['delivery_address__contact_number'],
            'id':"1",
            'orders': total_orders,
            'total_value': total_value
        })
        new_customer_order_list = sorted(new_customer_order_list, key=lambda k: k['orders'],reverse=True)
    
    return new_customer_order_list




def highest_value_customers(Customer):
    mobile_number = Order.objects.order_by('delivery_address__contact_number').values('delivery_address__contact_number').distinct()[:10]
    
    new_customer_order_list = []
    for item in mobile_number:
        total_orders = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).count()
        total_value = Order.objects.filter(delivery_address__contact_number = item['delivery_address__contact_number']).aggregate(total_price=Sum('total'))['total_price']
        name_list = DeliveryAddress.objects.values('sender_fullname').filter(contact_number=item['delivery_address__contact_number'])
        if total_value:
            total_value = total_value
        else:
            total_value = 0
        
        new_customer_order_list.append({
            'name': name_list[0]['sender_fullname'],
            'mobile': item['delivery_address__contact_number'],
            'id':"1",
            'orders': total_orders,
            'total_value': total_value
        })
        new_customer_order_list = sorted(new_customer_order_list, key=lambda k: k['total_value'],reverse=True)
    
    return new_customer_order_list


'''Sales Analytics'''


def total_sales_count_paid_cod_in_date(date):
    # print(Order.objects.filter(created_on__date=date,o_status="PE").count())

    return Order.objects.filter(created_on__date=date, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).aggregate(total_price=Sum('total')), Order.objects.filter(
        created_on__date=date, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).count(), Order.objects.filter(created_on__date=date, payment_status="Paid").aggregate(
        total_price=Sum('total')), Order.objects.filter(created_on__date=date, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status="Awaiting Payment").aggregate(
        total_price=Sum('total')),Order.objects.filter(
        created_on__date=date,payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).count(),Order.objects.filter(
        created_on__date=date,payment_status="Paid").count()


def total_sales_count_paid_cod_in_week(week):
    return Order.objects.filter(created_on__week=week, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).aggregate(total_price=Sum('total')), Order.objects.filter(
        created_on__week=week, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).count(), Order.objects.filter(created_on__week=week, payment_status="Paid").aggregate(
        total_price=Sum('total')), Order.objects.filter(created_on__week=week, payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).aggregate(
        total_price=Sum('total')), Order.objects.filter(
        created_on__week=week,payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).count(), Order.objects.filter(
        created_on__week=week,payment_status="Paid").count()


def total_sales_count_paid_cod_in_month(month):
    return Order.objects.filter(created_on__month=month, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).aggregate(total_price=Sum('total')), Order.objects.filter(
        created_on__month=month, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).count(), Order.objects.filter(created_on__month=month, payment_status="Paid").aggregate(
        total_price=Sum('total')), Order.objects.filter(created_on__month=month, payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).aggregate(
        total_price=Sum('total')),Order.objects.filter(
        created_on__month=month,payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).count(),Order.objects.filter(
        created_on__month=month,payment_status="Paid").count()


def total_sales_count_paid_cod_in_year(year):
    return Order.objects.filter(created_on__year=year, order_status__in=['Confirmed','Processing','Dispatched','Complete'], payment_status__in=['Awaiting Payment', 'Paid']).aggregate(total_price=Sum('total')), Order.objects.filter(
        created_on__year=year, order_status__in=['Confirmed','Processing','Dispatched','Complete'],  payment_status__in=['Awaiting Payment', 'Paid']).count(), Order.objects.filter(created_on__year=year, payment_status="Paid", order_status__in=['Confirmed','Processing','Dispatched','Complete']).aggregate(
        total_price=Sum('total')), Order.objects.filter(created_on__year=year, payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).aggregate(
        total_price=Sum('total')),Order.objects.filter(created_on__year=year,payment_status="Awaiting Payment", order_status__in=['Confirmed','Processing','Dispatched','Complete']).count(),Order.objects.filter(
        created_on__year=year,payment_status="Paid", order_status__in=['Confirmed','Processing','Dispatched','Complete']).count()


def best_selling_product_list(date):
    best_selling_product = ProductVarient.objects.filter(product_varient__order__created_on__date=date).annotate(
        order=Sum('product_varient__total')).order_by('-order')[:10]
    best_selling_product_list = []
    for product in best_selling_product:
        best_selling_product_list.append({
            'name': product.product.name+" - "+product.varient_name,
            'id': product.product.id,
            'store_slug':product.product.store.slug,
            'category': product.product.category.all(),
            # 'price': Product.objects.filter(id=product.id, orders__order__created_on__date=date).aggregate(
            #     total_sold=Sum('orders__total'))['total_sold'],
            'price': product.selling_price,
            'status': "In Stock" if product.quantity > 0 else "Out of Stock",
        })
    return best_selling_product_list


def best_selling_product_week(date):
    best_selling_product = ProductVarient.objects.filter(product_varient__order__created_on__week=date).annotate(
        order=Sum('product_varient__total')).order_by('-order')[:10]
    best_selling_product_list = []
    for product in best_selling_product:
        best_selling_product_list.append({
            'name': product.product.name+" - "+product.varient_name,
            'id': product.product.id,
            'store_slug':product.product.store.slug,
            'category': product.product.category.all(),
            'price': product.selling_price,
            'status': "In Stock" if product.quantity > 0 else "Out of Stock",
        })
    return best_selling_product_list


def best_selling_product_year(date):
    best_selling_product = ProductVarient.objects.filter(product_varient__order__created_on__year=date).annotate(
        order=Sum('product_varient__total')).order_by('-order')[:10]
    best_selling_product_list = []
    for product in best_selling_product:
        best_selling_product_list.append({
            'name': product.product.name+" - "+product.varient_name,
            'id': product.product.id,
            'store_slug':product.product.store.slug,
            'category': product.product.category.all(),
            'price': product.selling_price,
            'status': "In Stock" if product.quantity > 0 else "Out of Stock",
        })
    # print(best_selling_product_list)
    
    return best_selling_product_list


def best_selling_product_month(date):
    best_selling_product = ProductVarient.objects.filter(product_varient__order__created_on__month=date).annotate(
        order=Sum('product_varient__total')).order_by('-order')[:10]
    best_selling_product_list = []
    for product in best_selling_product:
        best_selling_product_list.append({
            'name': product.product.name+" - "+product.varient_name,
            'id': product.product.id,
            'store_slug':product.product.store.slug,
            'category': product.product.category.all(),
            'price': product.selling_price,
            'status': "In Stock" if product.quantity > 0 else "Out of Stock",
        })
    return best_selling_product_list


