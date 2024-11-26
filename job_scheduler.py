#### Schedule task with crone job to repost failure data to odoo
from sales.models import Order, OrderDelivery
from sales.utility import sendOrderToOdoo
from datetime import datetime

def CronJobScheduler():
    try:
        dt = "2022-07-17"
        # date = dt.strftime('%Y-%m-%d')
        order_detail = Order.objects.filter(odoo_status__in = ["Failed"]).order_by("id").values('id')[:30]
        if order_detail:
            for i in order_detail:
                order_id = i['id']
                rider = OrderDelivery.objects.filter(order__order_number=order_id).values('user__username', 'user__profile__phone_number', 'user__email')
                if rider:
                    rider_name = rider[0].get('user__username')
                    rider_phone = rider[0].get('user__profile__phone_number')
                    rider_email = rider[0].get('user__email')
                else:
                    rider_name = None
                    rider_phone = None
                    rider_email = None
                
                # odoo, error = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email, "Santosh", "santosh@ohocake.com")
                # Order.objects.filter(id=order_id).update(odoo_status=odoo)
                # status, error = sendOrderToOdoo(order_id, rider_name)
                # ord = Order.objects.filter(id=order_id).update(odoo_status=status)
        else:
            print("No Failure case till Now")
    except Exception as e:
        print(str(e), "error")