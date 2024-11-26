from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import *
from .forms import *
from django.contrib.auth.models import User
from django.conf import settings as conf
# from django.contrib.auth.decorators import permission_required
from accounts.views import custom_permission_required as permission_required,SuperUserCheck

# Create your views here.

@permission_required('settings.add_settings',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def settingsCreate(request):
	if request.method=='GET':
		if not User.objects.filter(username= conf.DELIVERY_API_USERNAME).exists():
			User.objects.create_user(username=conf.DELIVERY_API_USERNAME,
                                 email=conf.DELIVERY_API_EMAIL,
                                 password=conf.DELIVERY_API_PASSWORD,is_staff=True)
		settings = Settings.objects.last()
		form = SettingsForm() if not settings else SettingsForm(request.POST or None,instance=settings)
		return render(request,'admin_view/settings-form.html',{'form':form,'settings':settings})
	
	if request.method == 'POST':
		settings = Settings.objects.last()
		if not settings:
			form = SettingsForm(request.POST)
			if form.is_valid():
				form.save()
				return redirect('settings:settings-view')
		else:
			form = SettingsForm(request.POST,request.FILES,instance=settings)
			request_image_logo = request.POST.get('image-logo')
			request_image_banner = request.POST.get('image-banner')
			request_image_aggregator = request.POST.get('image-aggregator')
			if form.is_valid():
				settings_form = form.save(commit=False)
			
				if not request_image_logo is None:
					settings_form.outlet_logo.delete(save=True)
				
				if not request_image_aggregator is None:
					settings_form.aggregator_image.delete(save=True)
				
				if not request_image_banner is None:
					settings_form.banner_image.delete(save=True)
				
				settings_form.save()
				return redirect('settings:settings-view')
		return render(request,'admin_view/settings-form.html',{'form':form})

@permission_required('settings.view_settings',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def settingsView(request):
	if request.method=='GET':
		settings = Settings.objects.last()
		return render(request,'admin_view/settings.html',{'settings':settings})
	

@permission_required('settings.view_outletbranch',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def outletBranchList(request):
	if request.method=='GET':
		outlet_branch=OutletBranch.objects.order_by('-id')
		form=OutletForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			outlet_branch=OutletBranch.objects.filter(Q(branch_name__icontains=keywords))
		return render(request,'admin_view/outlet_branch.html',{'outlet_branch':outlet_branch,'keywords':keywords,'form':form})

@permission_required('settings.add_outletbranch',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def outletBranchAjaxCreate(request):
    if request.method == 'POST':
    	form = OutletForm(request.POST)
    	if form.is_valid():
    		form.save()
    		messages.success(request, "Outlet Branch has been Added Successfully")
    		return JsonResponse({'status': 'success'})
    	return JsonResponse({'errors': form.errors})


@permission_required('settings.change_outletbranch',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def outletBranchAjaxUpdate(request,pk):
	if request.method=='GET':
		outlet_branch=get_object_or_404(OutletBranch,id=pk)
		return JsonResponse({'status':'success','addons':model_to_dict(outlet_branch)})

	if request.method == 'POST':
		outlet_branch= get_object_or_404(OutletBranch,id=pk)
		form=OutletForm(request.POST,instance=outlet_branch)
		is_active_outlet_branch=request.POST.get('is_active_outlet_branch',None)
		is_active_outlet_branch=True if is_active_outlet_branch else False
		if form.is_valid():
			attachment=form.save(commit=False)
			attachment.is_active=is_active_outlet_branch
			attachment.save()
			messages.success(request, "Outlet Branch has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})
@permission_required('settings.delete_outletbranch',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteOutletBranchBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            outlet_branch=OutletBranch.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected outlet branch has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('settings.delete_outletbranch',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def outletBranchDelete(request,pk):
	if request.method=='POST':
		outlet_branch=get_object_or_404(OutletBranch,id=pk).delete()
		messages.success(request, "Outlet Branch has been removed successfully.")
		return redirect('settings:outlet-branch-list')


@permission_required('settings.add_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def create_shipping_method(request):
	from datetime import datetime
	if request.method == "POST":
		shipping_method_name = request.POST.get('shipping_method_name',None)
		shipping_method_price = request.POST.get('shipping_method_price',None)
		shipping_method_active = request.POST.get('shipping_method_active',False)
		shipping_display_order = request.POST.get('display_order_shipping',1)
		shipping_method_active = True if shipping_method_active else False
		shipping_time_from =  request.POST.getlist('shipping_time_from',None)
		shipping_time_to =  request.POST.getlist('shipping_time_to',None)
		shipping_time_active = request.POST.getlist('shipping_time_active',None)
		shipping_time_display_order = request.POST.getlist('display_order_time',1)
		if shipping_method_name and shipping_method_price:
			shipping_method = ShippingMethod.create_shipping_method(shipping_method_name,shipping_method_price,shipping_method_active,shipping_display_order)
			for count,item in enumerate(shipping_time_from):
				time_active = True if shipping_time_active[count] == "True" else False
				time = ShippingTime.create_shipping_time(datetime.strptime(shipping_time_from[count], '%H:%M'),datetime.strptime(shipping_time_to[count], '%H:%M'),time_active,shipping_time_display_order[count])
				ShippingMethod.add_shipping_time(shipping_method,time)
		messages.success(request, "Shipping Method added successfully.")
		return redirect('settings:shipping-method-list')
	return render(request,'admin_view/shipping_methods.html',)
import pdb

@permission_required('settings.change_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def edit_shipping_method(request,pk):
	from datetime import datetime
	shipping_method_obj = ShippingMethod.objects.get(id=pk)
	
	if request.method == "POST":
		shipping_method_name = request.POST.get('shipping_method_name',None)
		shipping_method_price = request.POST.get('shipping_method_price',None)
		shipping_method_active = request.POST.get('shipping_method_active',False)
		shipping_display_order = request.POST.get('display_order_shipping',1)
		shipping_method_active = True if shipping_method_active else False
		shipping_time_from =  request.POST.getlist('shipping_time_from',None)
		shipping_time_to =  request.POST.getlist('shipping_time_to',None)
		shipping_time_active = request.POST.getlist('shipping_time_active',None)
		shipping_time_display_order = request.POST.getlist('display_order_time',1)
 
		if shipping_method_name and shipping_method_price:
			shipping_method = ShippingMethod.update_shipping_method(pk,shipping_method_name,shipping_method_price,shipping_method_active,shipping_display_order)
			time=shipping_method.shipping_time.all()
			for i in time:
				try:
					i.delete()
				except:
					continue
			for count,item in enumerate(shipping_time_from):
				if ShippingTime.objects.filter(time_from=shipping_time_from[count],time_to=shipping_time_to[count]).exists():
					continue
				time_active = True if shipping_time_active[count] == "True" else False
				time = ShippingTime.create_shipping_time(datetime.strptime(shipping_time_from[count], '%H:%M'),datetime.strptime(shipping_time_to[count], '%H:%M'),time_active,shipping_time_display_order[count])
				ShippingMethod.add_shipping_time(shipping_method,time)
		messages.success(request, "Shipping Method updated successfully.")
		return redirect('settings:shipping-method-list')
	return render(request,'admin_view/shipping_method_edit.html',{'shipping_method':shipping_method_obj})


@permission_required('settings.view_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def shippingMethodList(request):
	if request.method=='GET':
		shipping_method=ShippingMethod.objects.order_by('display_order')
		keywords=request.GET.get('keywords',None)
		if keywords:
			shipping_method=ShippingMethod.objects.filter(name__icontains=keywords)
		return render(request,'admin_view/shipping_method_list.html',{'shipping_method':shipping_method,'keywords':keywords})


@permission_required('settings.delete_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteShippingMethod(request,pk):
	ShippingMethod.deleteShippingMethod(pk)	
	messages.success(request, "Shipping method has been removed successfully.")
	return redirect(request.META['HTTP_REFERER'])

@permission_required('settings.delete_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteShippingMethodBulk(request):
    if request.method=='POST':
    	item_id=request.POST.getlist('foo',None)
    	ShippingMethod.bulkDelete(item_id)
    	messages.success(request, "Selected shipping methods has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])


@permission_required('settings.change_shippingmethod',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def shippingAvailableStatus(request):
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		ShippingMethod.updateActiveStatus(val,item)
		return JsonResponse({'message':'ShippingMethod has been updated.'})