from django.shortcuts import render
from sales.models import Order,OrderDelivery,OrderAssignedToVendor, Factories
from django.views.generic import TemplateView
from datetime import date as d, timedelta
from django.urls import reverse_lazy
from accounts.forms import CustomLoginForm
from django.contrib import messages, auth
from django.shortcuts import redirect,get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
from django.http import JsonResponse
from django.conf import settings
from accounts .models import UserProfile
from django.contrib.auth.models import User

# Create your views here.

class VendorView(LoginRequiredMixin,TemplateView):
	login_url = reverse_lazy("vendorAndDelivery:login-as-vendor")
	template_name='vendorAndDelivery/vendor.html'
	def get(self,request,*args,**kwargs):
		date_day = request.GET.get('date')
		if date_day == 'today':
			today =d.today()
		elif date_day == 'tomorrow':
			today = d.today()+timedelta(days =1)
		else:
			today = d.today()
		try:
			if self.request.user.profile.is_vendor and not self.request.user.profile.factory:
				orders=Order.objects.filter(date=today,order_status__in=['Confirmed','Processing','Dispatched']).order_by('-order_status','delivery_order__pickup_time')
				total_count=orders.count()
				return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day})
			elif self.request.user.profile.is_vendor and self.request.user.profile.factory:
				orders=Order.objects.filter(date=today,order_status__in=['Confirmed','Processing','Dispatched'], delivery_order__factory__id=request.user.profile.factory.id).order_by('-order_status','delivery_order__pickup_time')
				total_count=orders.count()
				return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, "factory":self.request.user.profile.factory.name})
			else:
				messages.error(request,'Permission denied.')
				return redirect('vendorAndDelivery:login-as-vendor')
		except:
			messages.error(request,'Invalid credential for vendor')
			return redirect(request,'vendorAndDelivery:login-as-vendor')
	
	def post(self, request, *args, **kwargs):
		user=request.user
		order_number = request.POST.get('order',None)
		order = get_object_or_404(Order, order_number=order_number)
		OrderAssignedToVendor.objects.create(order = order, user=user)
		return redirect(request.META['HTTP_REFERER'])

from django.db.models import Case, When
class DeliveryBoyView(LoginRequiredMixin,TemplateView):
	login_url = reverse_lazy("vendorAndDelivery:login-as-delivery-boy")
	template_name='vendorAndDelivery/deliveryboy.html'
	
	def get(self, request, *args, **kwargs):
		date_day = request.GET.get('date')
		if date_day == 'today':
			today =d.today()
		elif date_day == 'yesterday':
			today = d.today()-timedelta(days =1)
		else:
			today = d.today()
		factory = self.request.user.profile.factory
		if factory:
			self.request.user.profile.factory.name
		else:
			factory = None
		try:
			if self.request.user.id == self.kwargs['user'] and self.request.user.profile.is_delivery_person: 
				delivery_status=request.GET.get('delivery_status',None)
				store_select=int(request.GET.get('store',None)) if request.GET.get('store',None) else None
				# today=d.today()
				if store_select and delivery_status and not delivery_status=='None':
					orders=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing','Dispatched','Complete'],store_id=store_select,order__delivery_status=delivery_status).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
				
				elif not store_select and not delivery_status:
					orders=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing','Dispatched','Complete']).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
				elif not delivery_status == 'None':
					orders=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing','Dispatched','Complete'],order__delivery_status=delivery_status).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
				elif store_select and  not delivery_status:
					orders=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing','Dispatched','Complete'],store_id=store_select).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
				else:
					orders=OrderDelivery.objects.filter(user=self.kwargs['user'],pickup_date=today,order__order_status__in=['Processing','Dispatched','Complete']).order_by(Case(When(order__delivery_status = 'Complete',then = 5),default = 0))
				store=OrderDelivery.storeList(self.kwargs['user'],today)
				total_count=orders.count()
				return render(request, self.template_name, {'total_count':total_count,'orders':orders,'user':self.kwargs['user'],'store':store,'store_select':store_select,'delivery_status':delivery_status,'date_day':date_day, 'factory':factory})
			else:
				messages.error(request,'Permission denied.')
				return redirect('vendorAndDelivery:login-as-delivery-boy')
		except:
			messages.error(request,'Invalid credential for delivery boy')
			return redirect(request,'vendorAndDelivery:login-as-delivery-boy')
	  		

def deliveryBoyLogin(request):
    if request.method=='GET':
    	try:
	        if request.user.is_authenticated and request.user.profile.is_delivery_person:
	            return redirect('vendorAndDelivery:user-assigned-delivery',user=request.user.id)
	        form=CustomLoginForm()
	        return render(request,'vendorAndDelivery/login_deliveryBoy.html',{'form':form})
    	except:
    		form=CustomLoginForm()
    		messages.error(request,'Login from valid account for delivery boy.')
    		return render(request,'vendorAndDelivery/login_deliveryBoy.html',{'form':form})

    if request.method =='POST':
        form=CustomLoginForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            email=data['login']
            password=data['password']
            user = auth.authenticate(email=email, password=password)
            try:
	            if (user is not None) and (user.profile.is_delivery_person):
	                auth.login(request, user)
	                return redirect('vendorAndDelivery:user-assigned-delivery',user=user.id)
	            else:
	                messages.success(request, "Invalid Credentials")
	                return render(request,'vendorAndDelivery/login_deliveryBoy.html',{'form':form})
            except:
            	messages.error(request, "Invalid Credentials for delivery boy.")
            	return render(request,'vendorAndDelivery/login_deliveryBoy.html',{'form':form})

        else:
            form=CustomLoginForm(request.POST)
            return render(request,'vendorAndDelivery/login_deliveryBoy.html',{'form':form})


class OrderItemDeliveryStatusChange(LoginRequiredMixin,TemplateView):
	template_name='vendorAndDelivery/deliveryboy.html'
	def post(self, request, *args, **kwargs):
		from datetime import datetime as dt
		current_date_time = dt.now() + timedelta(hours=5.75)
		order_id=request.POST.get('order_id',None)
		delivery_status=request.POST.get('delivery_status',None)
		user=request.POST.get('user',None)
		order=get_object_or_404(Order,id=order_id)
		if str(order.delivery_order.user.id) == str(user):
			if delivery_status == "Complete":
				delivered_on_time = current_date_time
			else:
				delivered_on_time = None
			Order.objects.filter(id=order_id).update(delivery_status=delivery_status, order_status = 'Complete',delivered_on=delivered_on_time)#
			try:
				rider = OrderDelivery.objects.filter(order__order_number=order).values('user__username', 'user__profile__phone_number', 'user__email')
				if rider:
					rider_name = rider[0].get('user__username')
					rider_phone = rider[0].get('user__profile__phone_number')
					rider_email = rider[0].get('user__email')
				else:
					rider_name = None
					rider_phone = None
					rider_email = None
				odoo = None
				from sales.utility import sendOrderToOdoo
				odoo, error  = sendOrderToOdoo(order_id, rider_name, rider_phone, rider_email)
				Order.objects.filter(id=order_id).update(odoo_status=odoo)
			except:
				pass
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'error':'Permission denied.'})


class OrderItemPaymentMethodChange(LoginRequiredMixin,TemplateView):
	template_name='vendorAndDelivery/deliveryboy.html'
	def post(self, request, *args, **kwargs):
		order_number=request.POST.get('order_number',None)
		payment_method=request.POST.get('payment_method',None)
		user=request.POST.get('user',None)
		order=get_object_or_404(Order,order_number=order_number)
		if str(order.delivery_order.user.id) == str(user):
			Order.objects.filter(order_number=order_number).update(payment_method=payment_method)
			return JsonResponse({'status':'success'})
		else:
			return JsonResponse({'error':'Permission denied.'})

class OrderStatusChange(LoginRequiredMixin,TemplateView):
	template_name='vendorAndDelivery/vendor.html'
	def post(self, request, *args, **kwargs):

		order_number=request.POST.get('order_number',None)
		order_status=request.POST.get('order_status',None)
		user_id = request.POST.get('user', None)
		order=get_object_or_404(Order,order_number=order_number)
		# if str(order.delivery_order.user.id) == str(request.user.id):
		# Order.objects.filter(order_number=order_number).update(order_status=order_status)
		if order_status == "Dispatched":
			order_status = "baker"
		Order.update_order_status(order.id,order_status,remarks=None)
		try:
			Order.update_dispatcher(order.id, order_status, user_id)
		except Exception as e:
			print(e, "error")
		return JsonResponse({'status':'success'})
		# else:
		# 	return JsonResponse({'error':'Permission denied.'})


def vendorLogin(request):
    if request.method=='GET':
    	try:
		    if request.user.is_authenticated and request.user.profile.is_vendor:
		    	return redirect('vendorAndDelivery:get-vendor-order')
		    form=CustomLoginForm()
		    return render(request,'vendorAndDelivery/login_vendor.html',{'form':form})
    	except:
    		form=CustomLoginForm()
    		messages.error(request,'Login from valid account for vendor.')
    		return render(request,'vendorAndDelivery/login_vendor.html',{'form':form})

    if request.method =='POST':
        form=CustomLoginForm(request.POST)
        if form.is_valid():
        	data=form.cleaned_data
        	email=data['login']
        	password=data['password']
        	user = auth.authenticate(email=email, password=password)
        	try:
	        	if (user is not None) and (user.profile.is_vendor):
	        		auth.login(request, user)
	        		return redirect('vendorAndDelivery:get-vendor-order')
	        	else:
	        		messages.error(request, "Invalid Credentials")
	        		return render(request,'vendorAndDelivery/login_vendor.html',{'form':form})
        	except:
        		messages.error(request, "Invalid Credentials for vendor.")
        		return render(request,'vendorAndDelivery/login_vendor.html',{'form':form})
        else:
        	form=CustomLoginForm(request.POST)
        	return render(request,'vendorAndDelivery/login_vendor.html',{'form':form})


def productionManagerLogin(request):
	if request.method=='GET':
		form=CustomLoginForm()
		try:
			if request.user.is_authenticated and request.user.profile.is_production_manager:
				return redirect('vendorAndDelivery:get-production-manager')
			return render(request,'vendorAndDelivery/production_login.html',{'form':form})
		except:
			messages.error(request,'Login from valid account for production manager.')
			return render(request,'vendorAndDelivery/production_login.html',{'form':form})

	if request.method == 'POST':
		form=CustomLoginForm(request.POST)
		if form.is_valid():
			data=form.cleaned_data
			email=data['login']
			password=data['password']
			user = auth.authenticate(email=email, password=password)
			# try:
			if (user is not None) and (user.profile.is_production_manager):
				auth.login(request, user)
				return redirect('vendorAndDelivery:get-production-manager')
			else:
				messages.error(request, "Invalid Credentials")
				return render(request,'vendorAndDelivery/production_login.html',{'form':form})
			# except:
			# 	messages.error(request, "Invalid Credentials for production manager.")
			# 	return render(request,'vendorAndDelivery/production_login.html',{'form':form})
		else:
			form=CustomLoginForm(request.POST)
			return render(request,'vendorAndDelivery/production_login.html',{'form':form})


class ProductionManagerView(LoginRequiredMixin,TemplateView):
	login_url = reverse_lazy("vendorAndDelivery:login-as-production")
	template_name='vendorAndDelivery/production_manager.html'
	def get(self,request,*args,**kwargs):
		date_day = request.GET.get('date')
		if date_day == 'today':
			today =d.today()
		elif date_day == 'yesterday':
			today = d.today()-timedelta(days=1)
		elif date_day == 'tomorrow':
			today = d.today()+timedelta(days=1)
		else:
			today = d.today()
		try:
			if self.request.user.profile.is_production_manager and not self.request.user.profile.factory:
				orders=Order.objects.filter(date=today,order_status__in=['Confirmed','Processing','Dispatched','Complete']).order_by('-id')
				total_count=orders.count()
				return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day})
			elif self.request.user.profile.is_production_manager and self.request.user.profile.factory:
				orders=Order.objects.filter(date=today,order_status__in=['Confirmed','Processing','Dispatched','Complete'], delivery_order__factory__id=request.user.profile.factory.id).order_by('-id')
				total_count=orders.count()
				return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, 'factory':self.request.user.profile.factory.name})
			else:
				messages.error(request,'Permission denied.')
				return redirect('vendorAndDelivery:login-as-production')
		except:
			messages.error(request,'Invalid credential for vendor')
			return redirect(request,'vendorAndDelivery:login-as-production')


def loginMain(request):
	if request.method=='GET':
		return render(request,'vendorAndDelivery/login_main.html')


def dispatcherLogin(request):
    if request.method=='GET':
    	form=CustomLoginForm()
    	try:
	        if request.user.is_authenticated and request.user.profile.is_dispatcher:
	            return redirect('vendorAndDelivery:dispatcher-page')
	        return render(request,'vendorAndDelivery/login_dispatcher.html',{'form':form})
    	except:
    		messages.error(request,'Login from valid account for dispatcher.')
    		return render(request,'vendorAndDelivery/login_dispatcher.html',{'form':form})

    if request.method =='POST':
        form=CustomLoginForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            email=data['login']
            password=data['password']
            user = auth.authenticate(email=email, password=password)
            try:
	            if (user is not None) and (user.profile.is_dispatcher):
	                auth.login(request, user)
	                return redirect('vendorAndDelivery:dispatcher-page')
	            else:
	                messages.success(request, "Invalid Credentials")
	                return render(request,'vendorAndDelivery/login_dispatcher.html',{'form':form})
            except:
            	messages.error(request, "Invalid Credentials for delivery boy.")
            	return render(request,'vendorAndDelivery/login_dispatcher.html',{'form':form})
        else:
            return render(request,'vendorAndDelivery/login_dispatcher.html',{'form':form})


class OrderDispatcher(LoginRequiredMixin,TemplateView):
	login_url = reverse_lazy("vendorAndDelivery:login-as-dispatcher")
	template_name='vendorAndDelivery/dispatcher.html'
	def get(self,request,*args,**kwargs):
		form = AssignDeliveryForm()
		date_day = request.GET.get('date')
		assign = request.GET.get('assign')
		if date_day == 'today':
			today =d.today()
		elif date_day == 'yesterday':
			today = d.today()-timedelta(days=1)
		elif date_day == 'tomorrow':
			today = d.today()+timedelta(days =1)
		else:
			today = d.today()
		status = request.GET.get('status', None)
		status_time = request.GET.get('status_time', None)
		# if self.request.user.profile.factory:
		# 	print("true running")
		# 	orders = OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Processing','Dispatched','Complete'], factory__id=request.user.profile.factory.id).order_by('-order__created_on')
		# 	print(orders, self.request.user.profile.factory.name)
		# else:
		# 	print("None")
		try:
			if not self.request.user.profile.factory:
				factory = Factories.objects.all()
				factory_list = []
				for i in factory:
					data = {}
					data["factory_name"] = i.name
					data["order_count"] = OrderDelivery.objects.filter(order__date=today, factory__id=i.id).count()
					factory_list.append(data)
			else:
				factory_list = []
		except:
			factory_list = []
		try:
			if assign:
				if self.request.user.profile.is_dispatcher and self.request.user.profile.factory:
					if not status:
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Processing','Dispatched','Complete'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('-created_on')
						total_count=orders.count()

					if status == "Processing":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Processing'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Processing'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Dispatched":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Dispatched'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Dispatched'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Completed":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status_time == "ascending":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time__hour')
						total_count=orders.count()
						
					if status_time == "descending":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete'], factory__id=request.user.profile.factory.id).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete'], delivery_order__factory__id=request.user.profile.factory.id).exclude(delivery_order__user__id__in=del_ord).order_by('-delivery_order__expected_delivery_time__hour')
						total_count=orders.count()

					user_detail =OrderDelivery.objects.filter(order__date=today, order__order_status__in=['Processing','Dispatched','Complete'], factory__id=request.user.profile.factory.id).values('user__id', 'user__username').distinct()
					return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, 'form':form, 'assign':True, 'user_info':user_detail, "factory":self.request.user.profile.factory.name, "factory_list":factory_list})
				
				if self.request.user.profile.is_dispatcher and not self.request.user.profile.factory:
					if not status:
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Processing','Dispatched','Complete']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete']).exclude(delivery_order__user__id__in=del_ord).order_by('-created_on')
						total_count=orders.count()

					if status == "Processing":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Processing']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Processing']).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Dispatched":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Dispatched']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Dispatched']).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Completed":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete']).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status_time == "ascending":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete']).exclude(delivery_order__user__id__in=del_ord).order_by('delivery_order__expected_delivery_time__hour')
						total_count=orders.count()
						
					if status_time == "descending":
						del_ord=OrderDelivery.objects.filter(order__date=today,order__order_status__in=['Complete']).values_list('user__id')
						orders = Order.objects.filter(date=today,order_status__in=['Complete']).exclude(delivery_order__user__id__in=del_ord).order_by('-delivery_order__expected_delivery_time__hour')
						total_count=orders.count()

					user_detail =OrderDelivery.objects.filter(order__date=today, order__order_status__in=['Processing','Dispatched','Complete']).values('user__id', 'user__username').distinct()
					return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, 'form':form, 'assign':True, 'user_info':user_detail, "factory_list":factory_list})
				else:
					messages.error(request,'Permission denied.')
					return redirect('vendorAndDelivery:login-as-dispatcher')
			else:
				if self.request.user.profile.is_dispatcher and self.request.user.profile.factory:
					if not status:
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete'], delivery_order__factory__id=request.user.profile.factory.id).order_by('-created_on')
						total_count=orders.count()

					if status == "Processing":
						orders = Order.objects.filter(date=today,order_status__in=['Processing'], delivery_order__factory__id=request.user.profile.factory.id).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Dispatched":
						orders = Order.objects.filter(date=today,order_status__in=['Dispatched'], delivery_order__factory__id=request.user.profile.factory.id).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Completed":
						orders = Order.objects.filter(date=today,order_status__in=['Complete'], delivery_order__factory__id=request.user.profile.factory.id).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status_time == "ascending":
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete'], delivery_order__factory__id=request.user.profile.factory.id).order_by('delivery_order__expected_delivery_time__hour')
						total_count=orders.count()
						
					if status_time == "descending":
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete'], delivery_order__factory__id=request.user.profile.factory.id).order_by('-delivery_order__expected_delivery_time__hour')
						total_count=orders.count()

					user_detail =OrderDelivery.objects.filter(order__date=today, order__order_status__in=['Processing','Dispatched','Complete'], factory__id=request.user.profile.factory.id).values('user__id', 'user__username').distinct()
					return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, 'form':form, 'user_info':user_detail, "factory":self.request.user.profile.factory.name, "factory_list":factory_list})
				
				if self.request.user.profile.is_dispatcher and not self.request.user.profile.factory:
					if not status:
						orders=Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete']).order_by('-created_on')
						total_count=orders.count()
					if status == "Processing":
						orders = Order.objects.filter(date=today,order_status__in=['Processing']).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Dispatched":
						orders = Order.objects.filter(date=today,order_status__in=['Dispatched']).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()

					if status == "Completed":
						orders = Order.objects.filter(date=today,order_status__in=['Complete']).order_by('delivery_order__expected_delivery_time')
						total_count=orders.count()
					
					if status_time == "ascending":
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete']).order_by('delivery_order__expected_delivery_time__hour')
						total_count=orders.count()

					if status_time == "descending":
						orders = Order.objects.filter(date=today,order_status__in=['Processing','Dispatched','Complete']).order_by('-delivery_order__expected_delivery_time__hour')
						total_count=orders.count()

					user_detail =OrderDelivery.objects.filter(order__date=today, order__order_status__in=['Processing','Dispatched','Complete']).values('user__id', 'user__username').distinct()
					return render(request, self.template_name, {'total_count':total_count,'orders':orders,'date_day':date_day, 'form':form, 'user_info':user_detail, "factory_list":factory_list})
				else:
					messages.error(request,'Permission denied.')
					return redirect('vendorAndDelivery:login-as-dispatcher')
		except:
			messages.error(request,'Invalid credential for dispatcher')
			return redirect(request,'vendorAndDelivery:login-as-dispatcher')

from .forms import AssignDeliveryForm
class AssignDeliveryBoy(LoginRequiredMixin,TemplateView):
	login_url = reverse_lazy("vendorAndDelivery:assign-delivery-boy")
	template_name='vendorAndDelivery/assign-delivery-boy.html'
	
	def get(self, request, *args, **kwargs):
		if request.user.profile.is_dispatcher:
			order = Order.objects.get(id=self.kwargs['pk'])
			try:
				delivery_order = OrderDelivery.objects.get(order = order)
				form = AssignDeliveryForm(instance = delivery_order)
			except:
				form = AssignDeliveryForm()
			return super(AssignDeliveryBoy,self).get(request,form=form)
		messages.error(request,'Permission Denied')
		return redirect('vendorAndDelivery:login-as-dispatcher')

	def post(self, request, *args, **kwargs):
		if request.user.profile.is_dispatcher:
			order = Order.objects.get(id=self.kwargs['pk'])
			try:
				delivery_order = OrderDelivery.objects.get(order = order)
				form = AssignDeliveryForm(request.POST,instance = delivery_order)
			except:
				form = AssignDeliveryForm(request.POST)
			if form.is_valid():
				att=form.save(commit = False)
				att.store = order.store
				att.order = order
				att.save()
				try:
					rider = OrderDelivery.objects.filter(order__order_number=order).values('user__username', 'user__profile__phone_number', 'user__email')
					if rider:
						rider_name = rider[0].get('user__username')
						rider_phone = rider[0].get('user__profile__phone_number')
						rider_email = rider[0].get('user__email')
					else:
						rider_name = None
						rider_phone = None
						rider_email = None
					
					from sales.utility import sendOrderToOdoo
					odoo, error = sendOrderToOdoo(self.kwargs['pk'], rider_name, rider_phone, rider_email)
					Order.objects.filter(id=self.kwargs['pk']).update(odoo_status=odoo)
				except:
					pass
				return redirect('vendorAndDelivery:dispatcher-page')
			return super(AssignDeliveryBoy,self).get(request,form=form)
		messages.error(request,'Permission Denied')
		return redirect('vendorAndDelivery:login-as-dispatcher')

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseRedirect



# @login_required
# def assignOrderToVendor(request):
# 	user=request.user
# 	order_number = request.GET.get('order')
# 	OrderAssignedToVendor.objects.create(order__order_number = order_number, user=user)
# 	return HttpResponseRedirect(request.path_info)


def GetDeliveryUser(request):
	user_id  = request.GET.get('user')
	order_id = request.GET.get('order_id')
	delivery_info = get_object_or_404(OrderDelivery, order__id=order_id)#OrderDelivery.objects.filter(user__id=user_id)
	user_name = delivery_info.user.username
	id =user_id
	pickup_date = delivery_info.pickup_date
	pickup_time = delivery_info.pickup_time
	try:
		factory = delivery_info.factory.name
	except:
		factory = ""
	expected_delivery = delivery_info.expected_delivery_time
	remarks = delivery_info.remarks
	# if not factory:
	# 	factory = ""
	return JsonResponse({"id":id,"username":user_name,"pickup_date":pickup_date,"pickup_time":pickup_time,"factory":factory,"remarks":remarks, "expected_time":expected_delivery})



def getOrderUser(request):
	user_id = request.GET.get('user_id', None)
	date_day = request.GET.get('date')
	if date_day == 'today':
		today =d.today()
	elif date_day == 'yesterday':
		today = d.today()-timedelta(days=1)
	elif date_day == 'tomorrow':
		today = d.today()+timedelta(days =1)
	else:
		today = d.today()
	from datetime import datetime
	try:
		if user_id:
			data_array = []
			order = OrderDelivery.objects.filter(user__id=user_id, order__date=today)
			for data in order:
				data_dis = {}
				status = data.order.order_status
				order_number = data.order.order_number
				payment_method = data.order.payment_method
				costumer_name = data.order.delivery_address.receiver_fullname
				address = data.order.delivery_address.receiver_area
				city = data.order.delivery_address.receiver_city
				contact = data.order.delivery_address.receiver_contact_number1
				# delivered_at = (data.order.completed_on).replace(tzinfo=pytz.utc)
				delivered_at = (data.order.delivered_on)
				if delivered_at:
					format = '%Y-%m-%d %H:%M %p'
					delivered_time = datetime.strftime(delivered_at, format)
				else:
					delivered_time = None
				data_dis['payment_method'] = payment_method
				data_dis['costumer_name'] = costumer_name
				data_dis['order_number'] = order_number
				data_dis['delivered_at'] = delivered_time
				data_dis['address'] = address
				data_dis['contact'] = contact
				data_dis['status'] = status
				data_dis['city'] = city
				data_array.append(data_dis)
			return JsonResponse({'data':data_array, 'status':200})
		else:
			return JsonResponse({'error':'User Not Found'})
	except Exception as e:
		return JsonResponse({'error':"Rider is not Assigned Yet!"})
		