from django.shortcuts import render, redirect
from django.http.response import Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from client.views import place_normal_order
from sales.models import Order
from django.views.generic import TemplateView
import json
from django.utils.decorators import method_decorator

# import payment api
from smarttech_payment_api.khalti import verify_transaction_from_khalti
from smarttech_payment_api.esewa import verify_transaction_from_esewa
from smarttech_payment_api.ime import request_ime_pay_credentials,verify_transaction_from_ime
from smarttech_payment_api.nic import NICACardCheckout  


def calculate_total_amount(reference):
   order = Order.objects.filter(reference = reference)
   total=0
   for i in order:
      total=total+i.total
   return total

def get_order(reference):
   return Order.objects.filter(reference = reference)

def initiate_payment(reference):
   order = get_order(reference)
   order.update(payment_status="Initiated")

''' 
Response from khalti payment total amount is verified
'''
@csrf_exempt 
def khalti_payment(request):
   if request.method == "POST":   
      token = request.POST.get('token', None)
      order_response = place_normal_order(request)
      order = get_order(order_response['reference'])
      if order_response['status'] == "Success":
         total_amount = calculate_total_amount(order_response['reference'])
         response = verify_transaction_from_khalti(token,total_amount)
         if response["status"] == "success":
            order.update(payment_method="KHALTI",payment_status="Paid")
            return JsonResponse({"status":"success","reference":order_response['reference']})
         else:
            return JsonResponse({"status":"error","message":"Payment Failed."})
      else:
         return JsonResponse({"status":"error","message":order_response["message"]})

"""
Order is placed first and required Esewa fields for form is sent as JSON response to cart.html
"""
@csrf_exempt
def initiate_esewa_payment_order(request):
   if request.method == "POST":
      order_response = place_normal_order(request)
      if order_response['status'] == "Success":
         initiate_payment(order_response['reference'])
         total_amount = calculate_total_amount(order_response['reference'])
         return JsonResponse({"reference":order_response['reference'],"status":"Success","total":total_amount})
      else:
         return JsonResponse({"message":order_response["message"],"status":"failed"})




"""
Response from esewa where we verify amount
"""
@csrf_exempt
def esewa_payment(request):
   if request.method == "GET":   
      ref = request.GET.get('oid','')
      order = Order.objects.filter(reference = ref)
      total_amount = calculate_total_amount(ref)
      response = verify_transaction_from_esewa(request,total_amount)
      if response["status"] == "success":
         order.update(payment_status="Paid",payment_method="ESEWA")
         return redirect('client:order-success',reference=ref)
      else:
         return redirect('payment:card-checkout-cancelled')
   else:
      return JsonResponse({"status":"error","message":response["message"]})



"""
Order is placed first and required IME fields for form is sent as JSON response to cart.html
"""
@csrf_exempt
def request_ime_credentials(request):
   if request.method == "POST":
      order_response = place_normal_order(request)
      if order_response['status'] == "Success":
         reference_number = order_response['reference']
         total_amount = calculate_total_amount(reference_number)
         print(reference_number)
         response = request_ime_pay_credentials(request, total_amount,reference_number)
         print("form",response['message']['response'])
         if response["status"] == "success":
            initiate_payment(order_response['reference'])
            return JsonResponse({"status":"success","form":response['message']['response'],"reference":reference_number})
         else:
            return JsonResponse({"status":"error","message":response["message"]})
      else:
         return JsonResponse({"message":order_response["message"],"status":"error"})
"""
Response from ime where we verify amount
"""
@csrf_exempt
def ime_payment(request):
   if request.method == "POST":   
      ref = request.POST.get('RefId','')
      total_amount = calculate_total_amount(ref)
      order = Order.objects.filter(reference=ref)
      response = verify_transaction_from_ime(request,total_amount)
      if response["status"] == "success":
         order.update(payment_status="Paid",payment_method="IME")
         return redirect('client:order-success',reference=ref)
      else:
         return redirect('payment:card-checkout-cancelled')


"""
Order is placed first and required NIC fields for form is sent as JSON response to cart.html
"""
class NICPayment(TemplateView,NICACardCheckout):
   template_name = 'client/cake-977/abc.html'
   def post(self, request, *args):
      
      order_response = place_normal_order(request)
      if order_response['status'] == "Success":
         order = Order.objects.filter(reference = order_response['reference'])[0]
         total_amount = calculate_total_amount(order_response['reference'])
         data = {
         'amount':total_amount,
         'email':order.delivery_address.sender_email,
         'mobile':order.delivery_address.contact_number,
         'reference_number':order.reference,
         'bill_to_forename':order.delivery_address.sender_fullname,
         'bill_to_address_line1':order.delivery_address.sender_address,
         }
         form_data = self.form_request(data)
         initiate_payment(order_response['reference'])
         return JsonResponse({'form':form_data,"reference":order_response['reference']})
      else:
         return JsonResponse({"message":order_response["message"],"status":"failed"})
      
      

   
"""
Response from NIC where we verify amount
"""
@method_decorator(csrf_exempt, name='dispatch')
class NICPaymentResponse(TemplateView,NICACardCheckout):
   
   def post(self, request):
      nic_response = self.verify_txn_at_bank(request.POST)
      order = Order.objects.filter(reference = nic_response['req_reference_number'])
      reason_code = nic_response['reason_code']
      total_amount = calculate_total_amount(nic_response['req_reference_number'])
      if (float(nic_response['req_amount']) == float(total_amount)) and reason_code == "100":
         order.update(payment_status="Paid",payment_method="CARD")
      return redirect('client:order-success',reference=nic_response['req_reference_number'])


"""
Redirect url when nic/ime transaction is cancelled or fails
"""
@csrf_exempt
def nic_checkout_cancelled(request):
   template_name = 'client/cake-977/payment_failed.html'
   return render(request,template_name,)


"""
Redirect url when ime transaction is cancelled or fails
"""
@csrf_exempt
def ime_checkout_cancelled(request):
   if request.method == "POST":
      template_name = 'client/cake-977/payment_failed.html'
      return render(request,template_name,)