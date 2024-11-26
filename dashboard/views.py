
from django.views.generic import TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages, auth
# from admin_account.views import SuperUserCheck
from django.utils import timezone
from datetime import timedelta
from .dashboardcallback import *
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q
from accounts.views import custom_permission_required as permission_required,SuperUserCheck
    
class AdminDashboard(SuperUserCheck,TemplateView):
    template_name = "admin_view/dashboard/dashboard.html"
    
    def __init__(self):
        self.Customer = get_user_model()
        self.today_date = timezone.now()
        self.yesterday_date = timezone.now() - timedelta(days=1)
        self.today_week = timezone.now().isocalendar()[1]
        self.today_month = timezone.now().month
        self.today_year = timezone.now().year

        super(AdminDashboard, self).__init__()

    def get(self, request, **kwargs):
        
        storage = messages.get_messages(request)
        storage.used = True

        # Recent Orders
        recent_orders = most_recent_orders()
        # Customers
        new_customer_order_list = first_time_customers(self.Customer)
        highest_customer_order = most_orders_customers(self.Customer)
        highest_value_customer = highest_value_customers(self.Customer)

        # # Sales today
        total_sales_today, total_sales_order_count_today, total_sales_paid_today, total_sales_cod_today,today_pending,today_paid = total_sales_count_paid_cod_in_date(
            self.today_date)
        best_selling_product_today_list = best_selling_product_list(self.today_date)
        # most_ordered_product_today_list = most_ordered_product(self.today_date)

        # # Sales Yesterday
        total_sales_yesterday, total_sales_yesterday_count, total_sales_paid_yesterday, total_sales_cod_yesterday,yes_pending,yes_paid = total_sales_count_paid_cod_in_date(
            self.yesterday_date)
        best_selling_product_yesterday = best_selling_product_list(self.yesterday_date)
        # most_ordered_product_yesterday = most_ordered_product(self.yesterday_date)

        # # Sales Week
        total_sales_week, total_sales_week_count, total_sales_paid_week, total_sales_cod_week,week_pending,week_paid = total_sales_count_paid_cod_in_week(
            self.today_week)
        
        _best_selling_product_week = best_selling_product_week(self.today_week)
        # _most_ordered_product_week = most_ordered_product_week(self.today_week)

        # # Sales month
        total_sales_month, total_sales_month_count, total_sales_paid_month, total_sales_cod_month,month_pending,month_paid = total_sales_count_paid_cod_in_month(
            self.today_month)
        _best_selling_product_month = best_selling_product_month(self.today_month)
        # _most_ordered_product_month = most_ordered_product_month(self.today_month)

        # # Sales year
        total_sales_year, total_sales_year_count, total_sales_paid_year, total_sales_cod_year,year_pending,year_paid = total_sales_count_paid_cod_in_year(
            self.today_year)
        _best_selling_product_year = best_selling_product_year(self.today_year)
        # _most_ordered_product_year = most_ordered_product_year(self.today_year)



        return super(AdminDashboard, self).get(request, recent_orders=recent_orders,
                                               new_customers=new_customer_order_list,
                                               most_order_customers=highest_customer_order,
                                               highest_value_customers=highest_value_customer,
                                               total_sales_today=total_sales_today,
                                               total_sales_paid_today=total_sales_paid_today,
                                               total_sales_cod_today=total_sales_cod_today,
                                               total_sales_order_count_today=total_sales_order_count_today,
                                               total_pending_sales_today = today_pending,
                                               total_paid_sales_today = today_paid,
                                               total_sales_yesterday_count=total_sales_yesterday_count,
                                               total_sales_yesterday=total_sales_yesterday,
                                               total_sales_cod_yesterday=total_sales_cod_yesterday,
                                               total_sales_paid_yesterday=total_sales_paid_yesterday,
                                               total_order_pending_yesterday = yes_pending,
                                               total_order_paid_yesterday = yes_paid,
                                               total_sales_week=total_sales_week,
                                               total_sales_week_count=total_sales_week_count,
                                               total_sales_paid_week=total_sales_paid_week,
                                               total_sales_cod_week=total_sales_cod_week,
                                               week_pending_count = week_pending,
                                               week_paid_count = week_paid,
                                               total_sales_month=total_sales_month,
                                               total_sales_month_count=total_sales_month_count,
                                               total_sales_paid_month=total_sales_paid_month,
                                               total_sales_cod_month=total_sales_cod_month,
                                               month_pending_count = month_pending,
                                               month_paid_count = month_paid,
                                               total_sales_year=total_sales_year,
                                               total_sales_year_count=total_sales_year_count,
                                               total_sales_paid_year=total_sales_paid_year,
                                               total_sales_cod_year=total_sales_cod_year,
                                               year_pending_count = year_pending,
                                               year_paid_count = year_paid,
                                               best_selling_product_today=best_selling_product_today_list,
                                               best_selling_product_yesterday = best_selling_product_yesterday,
                                               best_selling_product_week = _best_selling_product_week,
                                               best_selling_product_month=_best_selling_product_month,
                                               best_selling_product_year = _best_selling_product_year,
                                              
                                               )


@permission_required('auth.view_user',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def get_all_customers(request):
    customers_obj = get_user_model()
    keyword = request.GET.get('customer_keyword',None)
    if keyword:
      orders=Order.objects.filter(Q(delivery_address__contact_number__icontains=keyword)|Q(delivery_address__full_name__icontains=keyword)).order_by('delivery_address__contact_number').distinct('delivery_address__contact_number')
    else:
      orders=Order.objects.filter(order_status='Complete').order_by('delivery_address__contact_number').distinct('delivery_address__contact_number')
    return render(request,'admin_view/dashboard/customers.html',{'keyword':keyword,'orders':orders})







