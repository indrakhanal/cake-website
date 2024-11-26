from django.shortcuts import render,redirect
from django.http.response import Http404
from smarttech_payment_api.models import *
from sales.models import Order
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .forms import *
from django.contrib import messages


@user_passes_test(lambda u: u.is_superuser)
def paymentList(request):
   if request.method=='GET':
      khalti = KhaltiCredential.objects.last()
      esewa=EsewaCredential.objects.last()
      return render(request,'admin_view/payment/payment.html',{'khalti':khalti,'esewa':esewa})

@user_passes_test(lambda u: u.is_superuser)
def paymentCreate(request):
   if request.method=='GET':
      khalti = KhaltiCredential.objects.last()
      esewa=EsewaCredential.objects.last()
      
      if not khalti and not esewa:
         form1 = KhaltiCredentialForm()
         form2=EsewaCredentialForm()
      if khalti and esewa:
         form1 = KhaltiCredentialForm(request.POST or None,instance=khalti)
         form2=EsewaCredentialForm(request.POST or None,instance=esewa)
      if khalti and not esewa:
         form1 = KhaltiCredentialForm(request.POST or None,instance=khalti)
         form2=EsewaCredentialForm()
      if not khalti and esewa:
         form1 = KhaltiCredentialForm()
         form2=EsewaCredentialForm(request.POST or None,instance=esewa)

      return render(request,'admin_view/payment/payment_create.html',{'form1':form1,'form2':form2,'khalti':khalti,'esewa':esewa})
   
   if request.method=='POST':
      khalti = KhaltiCredential.objects.last()
      esewa=EsewaCredential.objects.last()
      is_active_khalti=request.POST.get('khalti',None)
      is_active_esewa=request.POST.get('esewa',None)
      if is_active_esewa=='True':
         is_active_esewa=True
      else:
         is_active_esewa=False

      if is_active_khalti=='True':
         is_active_khalti=True
      else:
         is_active_khalti=False

      if not khalti and not esewa:
         form1 = KhaltiCredentialForm(request.POST)
         form2=EsewaCredentialForm(request.POST)
      if khalti and esewa:
         form1 = KhaltiCredentialForm(request.POST or None,instance=khalti)
         form2=EsewaCredentialForm(request.POST or None,instance=esewa)
      if khalti and not esewa:
         form1 = KhaltiCredentialForm(request.POST or None,instance=khalti)
         form2=EsewaCredentialForm()
      if not khalti and esewa:
         form1 = KhaltiCredentialForm()
         form2=EsewaCredentialForm(request.POST or None,instance=esewa)
      
      if form1.is_valid() and form2.is_valid():
         attachment1=form1.save(commit=False)
         attachment1.is_active=is_active_khalti
         attachment1.save()
         attachment2=form2.save(commit=False)
         attachment2.is_active=is_active_esewa
         attachment2.save()
         messages.success(request, "Payment credentials added successfully.")
         return redirect('payment:payment-list')
      else:
         return render(request,'admin_view/payment/payment_create.html',{'form1':form1,'form2':form2,'khalti':khalti,'esewa':esewa})


@user_passes_test(lambda u: u.is_superuser,lambda u: u.is_staff)
def paymentAvailableStatus(request):
   if request.method=='GET':
      val=request.GET.get('val', None)
      item=request.GET.get('item-id', None)
      type_pay=request.GET.get('type', None)
      if type_pay == 'khalti':
         if val == 'True':
            is_active=True
         if val == 'False':
            is_active=False
         KhaltiCredential.objects.filter(id=item).update(is_active=is_active)
      if type_pay == 'esewa':
         if val == 'True':
            is_active=True
         if val == 'False':
            is_active=False
         EsewaCredential.objects.filter(id=item).update(is_active=is_active)
      return JsonResponse({'message':'Status updated.'})


def payment_failed(request):
   template_name = 'client/cake-977/payment_failed.html'
   return render(request,template_name,)


from client.views import BaseView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name='dispatch')
class PaymentFailedNIC(BaseView):
   # template_name = 'client/cake-977/payment_failed.html'

   def post(self, request, *args, **kwargs):
      return render(request, 'client/cake-977/payment_failed.html')