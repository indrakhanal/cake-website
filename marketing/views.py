from django.shortcuts import render
from .models import *
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from accounts.views import custom_permission_required as permission_required,SuperUserCheck
from catalog.models import Product,Category

# Create your views here.

@permission_required('marketing.view_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def couponList(request):
	if request.method=='GET':
		coupon=CartCoupon.objects.order_by('-id')
		coupon_types=request.GET.get('coupon_types',None)
		coupon_keywords=request.GET.get('coupon_keywords',None)

		if coupon_keywords:
			coupon=CartCoupon.objects.filter(Q(coupon_type__icontains=coupon_keywords) | Q(coupon_number__icontains=coupon_keywords)
				| Q(total_user_limit__icontains=coupon_keywords)
				| Q(per_user_limit__icontains=coupon_keywords)
				)
		if coupon_types and not coupon_types=='All':
			coupon=CartCoupon.objects.filter(coupon_type=coupon_types)
		return render(request,'admin_view/marketing/coupons/coupons.html',{'coupons':coupon,'coupon_types':coupon_types,'coupon_keywords':coupon_keywords})

@permission_required('marketing.delete_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def couponDelete(request,pk):
	if request.method=='POST':
		coupon=get_object_or_404(CartCoupon,id=pk)
		coupon.delete()
		messages.success(request, "Coupon has been removed successfully.")
		return redirect('marketing:coupons-list')

@permission_required('marketing.add_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def couponCreate(request):
	if request.method=='GET':
		category=Category.objects.all()
		product=Product.objects.all()
		form =CouponForm()
		return  render(request,'admin_view/marketing/coupons/coupons-create.html',{'form':form,'category':category,'product':product})
	if request.method=='POST':
		category=Category.objects.all()
		product=Product.objects.all()
		form=CouponForm(request.POST)
		time_limit=request.POST.get('time-limit',None)
		is_active=request.POST.get('radioInline',None)
		True if is_active=='True' else False
		if form.is_valid() and time_limit:
			attachment=form.save(commit=False)
			attachment.time_limit=time_limit
			attachment.is_active=is_active
			attachment.save()
			messages.success(request, "Coupon has been added successfully.")
			return redirect('marketing:coupons-list')
		if not time_limit:
			form.add_error(None,'Please select time limit date.')
		return render(request,'admin_view/marketing/coupons/coupons-create.html',{'form':form,'category':category,'product':product})

@permission_required('marketing.add_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def getCategoryProduct(request):
	from django.forms.models import model_to_dict
	if request.method=='GET':
		store_id=request.GET.get('store',None)
		product=list(Product.objects.filter(store_id=store_id).values('id','name'))
	return JsonResponse({'status':'Success','product':product})

@permission_required('marketing.update_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def couponUpdate(request,pk):
	if request.method=='GET':
		coupon=get_object_or_404(CartCoupon,id=pk)
		form=CouponForm(instance=coupon)
		return render(request,'admin_view/marketing/coupons/coupons-update.html',{'form':form,'coupon':coupon})
	if request.method=='POST':
		coupon=get_object_or_404(CartCoupon,id=pk)
		form=CouponForm(request.POST,instance=coupon)
		time_limit=request.POST.get('time-limit',None)
		is_active=request.POST.get('radioInline',None)
		if is_active=='True':
			is_active=True
		else:
			is_active=False
		if form.is_valid() and time_limit:
			attachment=form.save(commit=False)
			attachment.time_limit=time_limit
			attachment.is_active=is_active
			attachment.save()
			messages.success(request, "Coupon has been updated successfully.")
			return redirect('marketing:coupons-list')
		if not time_limit:
			form.add_error(None,'Please select time limit date.')
		return render(request,'admin_view/marketing/coupons/coupons-update.html',{'form':form,'coupon':coupon})


@permission_required('marketing.delete_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteCouponBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            coupon=CartCoupon.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected Coupons has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('marketing.change_cartcoupon',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def proAvailableStatus(request):
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		if val == 'True':
			is_available=True
		if val == 'False':
			is_available=False
		CartCoupon.objects.filter(id=item).update(is_active=is_available)
		return JsonResponse({'message':'Coupon has been updated.'})

