from .models import *
from django.shortcuts import render, redirect
from django.http.response import Http404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import *
import requests
import uuid
import base64
import json
from sales.models import Order
from settings.models import Settings


@csrf_exempt
def post_nepexpress(request):
    settings_ = Settings.objects.all().get()
    try:
        if request.method == "POST":
            settings_username = str(settings_.nepxpress_username)
            settings_password = str(settings_.nepxpress_password)
            print(settings_username, settings_password)
            username_bytes = bytes(settings_username, 'utf-8')
            password_bytes = bytes(settings_password, 'utf-8')

            b64ValUserPass = base64.b64encode(b":".join([username_bytes, password_bytes])).decode('utf-8')

            # b64ValUserPass = base64.b64encode(b":".join([b'60678A30-C9C3-4090-BD49-ABC0B648DDD5', b'demo'])).decode('utf-8')

            url = "http://developers.nepxpress.com/api/Client/RequestOrder"
            order_id = str(request.POST.get('order_id', None))
            branch_name = str(request.POST.get('branch_name', None))

            order = Order.objects.get(id=int(order_id))
            parcel = ""
            for item in order.items.all():
                parcel = parcel + str(item.product) + " X " + str(item.quantity) + " , "

            name = order.delivery_address.full_name
            address = order.delivery_address.delivery_address
            contact = order.delivery_address.contact_number
            quantity_int = int(order.get_order_products_count())
            order_number = order.order_number

            if order.discount:
                amount_int = int(order.discount_total())
            else:
                amount_int = int(order.total)
            comment = ""
            if branch_name:
                sender = branch_name + "( " + Settings.objects.all().get().outlet_name + " )"
            else:
                sender = Settings.objects.all().get().outlet_name

            sender_contact = Settings.objects.all().get().contact_number
            pickup_lat_lon = ""
            delivery_lat_long = ""
            weight_int = ""

            payload = {
                "OrderId": order_number,
                "Name": name,
                "Address": address,
                "Contact": contact,
                "Quantity": quantity_int,
                "Amount": amount_int,
                "Comment": comment,
                "Parcel": parcel,
                "Sender": sender,
                "SenderContact": sender_contact,
                "PickupLatang": pickup_lat_lon,
                "DeliveryLatang": delivery_lat_long,
                "Weight": weight_int
            }

            headers = {
                "Authorization": "Basic {}".format(b64ValUserPass),
                "Content-Type": "application/json"
            }

            if not order.delivery_sent_nepxpress:
                response = requests.post(url, data=json.dumps(payload), headers=headers)
                if response.status_code == 200:
                    order.delivery_sent_nepxpress = True
                    order.delivery_assigned = branch_name + " / " + "Nepxpress"
                    order.save()
                    return JsonResponse({'status': "Delivery details sent to nepxress ", 'code': "201"})
                else:
                    return JsonResponse(
                        {'status': "Something went wrong. Couldn't place order via nepxpress ", 'code': "500"})
            else:
                return JsonResponse(
                    {'status': "Delivery for this order has already been sent to nepxpress", 'code': "400"})

    except Exception as ex:
        return JsonResponse({'status': "Something went wrong. Couldn't place order via nepxpress ", 'code': "500"})


import json


def track_order(request):
    try:
        b64ValUserPass = base64.b64encode(b":".join([b'60678A30-C9C3-4090-BD49-ABC0B648DDD5', b'demo'])).decode('utf-8')
        url = "http://developers.nepxpress.com/api/Client/Track?OrderId=" + "ttt"

        headers = {
            "Authorization": "Basic {}".format(b64ValUserPass),
        }
        response = requests.post(url, headers=headers)
        return JsonResponse({'response': response.json()})

    except Exception as ex:
        return JsonResponse({'response': "Something went wrong"})
