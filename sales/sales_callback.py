from sales.models import Order
from django.db.models import Sum
from datetime import date
import csv
from django.http import HttpResponse




def sells_over_time_filter_date_range(date):
    total = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    item_count = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
    total_paid = Order.objects.filter(placed_on=date, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    total_unpaid = Order.objects.filter(placed_on=date,order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"], payment_status="Awaiting Payment").aggregate(total_price=Sum('total'))
    discounts = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
    shipping = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))
    
    if total['total_price'] is None:
        total['total_price'] = 0
    if discounts['total_price'] is None:
        discounts['total_price'] = 0
    if total_paid['total_price'] is None:
        total_paid['total_price']=0
    if total_unpaid['total_price'] is None:
        total_unpaid['total_price']=0
    if shipping['total_price'] is None:
        shipping['total_price']=0
    net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
    data = {
        # 'status':f'{start_date}-to-{end_date}',
        'total':total['total_price'],
        'item_count':item_count,
        'paid':total_paid['total_price'],
        'unpaid':total_unpaid['total_price'],
        'discount': discounts['total_price'],
        'shipping':shipping['total_price'],
        'net_sells': net_sells,
    }

    return data


def sells_over_time_week_month_and_yearly_basis(date,month, year):
        # date = cls.objects.values('placed_on')
        total = Order.objects.filter(placed_on__week=date,placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        item_count = Order.objects.filter(placed_on__week=date, placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
        total_paid = Order.objects.filter(placed_on__week=date,placed_on__month=month, placed_on__year=year, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        total_unpaid = Order.objects.filter(placed_on__week=date,placed_on__month=month, placed_on__year=year, payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        discounts = Order.objects.filter(placed_on__week=date, placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
        shipping = Order.objects.filter(placed_on__week=date, placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))

        if total['total_price'] is None:
            total['total_price'] = 0
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
        
        data={
            'total':total['total_price'],
            'item_count':item_count,
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'discount': discounts['total_price'],
            'shipping':shipping['total_price'],
            'net_sells':net_sells
        }
        return data


def sells_over_time_month_and_yearly_basis(month, year):
        # date = cls.objects.values('placed_on')
      
        total = Order.objects.filter(placed_on__month=month, placed_on__year=year,order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        item_count = Order.objects.filter(placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
        total_paid = Order.objects.filter(placed_on__month=month, placed_on__year=year, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        total_unpaid = Order.objects.filter(placed_on__month=month, placed_on__year=year, payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        discounts = Order.objects.filter(placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
        shipping = Order.objects.filter(placed_on__month=month, placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))

        if total['total_price'] is None:
            total['total_price'] = 0
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
        data = {
            'total':total['total_price'],
            'item_count':item_count,
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'discount': discounts['total_price'],
            'shipping':shipping['total_price'],
            'net_sells':net_sells
        }
        return data


def sells_over_time_monthly(month):
        # date = cls.objects.values('placed_on')
      
        total = Order.objects.filter(placed_on__month=month, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        item_count = Order.objects.filter(placed_on__month=month, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
        total_paid = Order.objects.filter(placed_on__month=month, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        total_unpaid = Order.objects.filter(placed_on__month=month,  payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
        discounts = Order.objects.filter(placed_on__month=month, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
        shipping = Order.objects.filter(placed_on__month=month, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))

        if total['total_price'] is None:
            total['total_price'] = 0
        if discounts['total_price'] is None:
            discounts['total_price'] = 0
        if total_paid['total_price'] is None:
            total_paid['total_price']=0
        if total_unpaid['total_price'] is None:
            total_unpaid['total_price']=0
        if shipping['total_price'] is None:
            shipping['total_price']=0
        net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
        data = {
            'total':total['total_price'],
            'item_count':item_count,
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'discount': discounts['total_price'],
            'shipping':shipping['total_price'],
            'net_sells':net_sells
        }
        return data

def sells_over_time_yearly_basis(year):
    total = Order.objects.filter( placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    item_count = Order.objects.filter(placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
    total_paid = Order.objects.filter( placed_on__year=year, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    total_unpaid = Order.objects.filter( placed_on__year=year, payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    discounts = Order.objects.filter( placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
    shipping = Order.objects.filter(placed_on__year=year, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))

    if total['total_price'] is None:
        total['total_price'] = 0
    if discounts['total_price'] is None:
        discounts['total_price'] = 0
    if total_paid['total_price'] is None:
        total_paid['total_price']=0
    if total_unpaid['total_price'] is None:
        total_unpaid['total_price']=0
    if shipping['total_price'] is None:
        shipping['total_price']=0
    net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])

    data = {
            'total':total['total_price'],
            'item_count':item_count,
            'paid':total_paid['total_price'],
            'unpaid':total_unpaid['total_price'],
            'discount': discounts['total_price'],
            'shipping':shipping['total_price'],
            'net_sells':net_sells
        }
    return data

def sells_over_time_filter_date_range(date):
    total = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    item_count = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
    total_paid = Order.objects.filter(placed_on=date, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    total_unpaid = Order.objects.filter(placed_on=date, payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    discounts = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
    shipping = Order.objects.filter(placed_on=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))
    
    if total['total_price'] is None:
        total['total_price'] = 0
    if discounts['total_price'] is None:
        discounts['total_price'] = 0
    if total_paid['total_price'] is None:
        total_paid['total_price']=0
    if total_unpaid['total_price'] is None:
        total_unpaid['total_price']=0
    if shipping['total_price'] is None:
        shipping['total_price']=0
    net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
    data = {
        # 'status':f'{start_date}-to-{end_date}',
        'total':total['total_price'],
        'item_count':item_count,
        'paid':total_paid['total_price'],
        'unpaid':total_unpaid['total_price'],
        'discount': discounts['total_price'],
        'shipping':shipping['total_price'],
        'net_sells': net_sells,
    }

    return data


def sells_over_time_filter_week(date):
    total = Order.objects.filter(placed_on__week=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    item_count = Order.objects.filter(placed_on__week=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).count()
    total_paid = Order.objects.filter(placed_on__week=date, payment_status="Paid", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    total_unpaid = Order.objects.filter(placed_on__week=date, payment_status="Awaiting Payment", order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('total'))
    discounts = Order.objects.filter(placed_on__week=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('discount'))
    shipping = Order.objects.filter(placed_on__week=date, order_status__in=["Processing", "Confirmed", "Complete", "Dispatched"]).aggregate(total_price=Sum('shipping_cost'))
    
    if total['total_price'] is None:
        total['total_price'] = 0
    if discounts['total_price'] is None:
        discounts['total_price'] = 0
    if total_paid['total_price'] is None:
        total_paid['total_price']=0
    if total_unpaid['total_price'] is None:
        total_unpaid['total_price']=0
    if shipping['total_price'] is None:
        shipping['total_price']=0
    net_sells = (total_paid['total_price']+total_unpaid['total_price']+shipping['total_price']-discounts["total_price"])
    data = {
        # 'status':f'{start_date}-to-{end_date}',
        'total':total['total_price'],
        'item_count':item_count,
        'paid':total_paid['total_price'],
        'unpaid':total_unpaid['total_price'],
        'discount': discounts['total_price'],
        'shipping':shipping['total_price'],
        'net_sells': net_sells,
    }
    return data

def week_from_date(date_object):
    date_ordinal = date_object.toordinal()
    year = date_object.year
    week = ((date_ordinal - _week1_start_ordinal(year)) // 7) + 1
    if week >= 52:
        if date_ordinal >= _week1_start_ordinal(year + 1):
            year += 1
            week = 1
    return year, week

def _week1_start_ordinal(year):
    jan1 = date(year, 1, 1)
    jan1_ordinal = jan1.toordinal()
    jan1_weekday = jan1.weekday()
    week1_start_ordinal = jan1_ordinal - ((jan1_weekday + 1) % 7)
    return week1_start_ordinal


def export_csv_file_sells_over_time(new_list, title):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sells_report.csv"'
    writer = csv.writer(response)
    writer.writerow(title)
    for data in new_list:
        writer.writerow(data.values())
    return response



def product_selling_today(date):
    order_number = Order.objects.filter(placed_on=date).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list

def product_sells_week(date):
    order_number = Order.objects.filter(placed_on__week=date).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list


def product_sells_month(date):
    order_number = Order.objects.filter(placed_on__month=date).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list

def product_sells_years(date):
    order_number = Order.objects.filter(placed_on__year=date).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list

def product_sells_in_date_range(start_date, end_date):
    order_number = Order.objects.filter(placed_on__range=[start_date,end_date]).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list


def product_sells_in_date(start_date):
    order_number = Order.objects.filter(placed_on=start_date).values_list('id')
    return order_number
    # order_list = []
    # for item in order_number:
    #     order_list.append(item['order_number'])
    # return order_list


from datetime import datetime, timedelta
# import datetime

def date_range(start, end):
    delta = end - start 
    days = [start + timedelta(days=i) for i in range(delta.days + 1)]
    return days


def find_weeks(start,end):
    l = []
    for i in range((end-start).days + 1):
        d = (start+timedelta(days=i)).isocalendar()[:2]
        yearweek = '{}{:02}'.format(*d)
        l.append(yearweek)
    return sorted(set(l))



def months_between(start,end):
    months = []
    cursor = start

    while cursor <= end:
        if cursor.month not in months:
            months.append(cursor.month)
        cursor += timedelta(weeks=1)

    return months


def calculate_all_month_in_year_range(date1, date2):
    import calendar
    date1 = date1.replace(day = 1)
    date2 = date2.replace(day = 1)
    # months_str = calendar.month
    months = []
    while date1 < date2:
        month = date1.month
        year  = date1.year
        months.append("{0}-{1}".format(month,year))
        next_month = month+1 if month != 12 else 1
        next_year = year + 1 if next_month == 1 else year
        date1 = date1.replace( month = next_month, year= next_year)
    return months



def weeknum_to_dates(weeknum, year):
    return [datetime.strptime(f"{year}-W"+ str(weeknum) + str(x), "%Y-W%W-%w").strftime('%Y-%m-%d') for x in range(-5,0)]



