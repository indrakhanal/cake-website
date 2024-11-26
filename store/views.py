from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView
from .models import *
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404,JsonResponse
from .forms import *
from django.contrib import messages
from django.forms.models import model_to_dict
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# from django.contrib.auth.decorators import permission_required
from accounts.views import custom_permission_required as permission_required,SuperUserCheck

# Create your views here.


@permission_required('store.view_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeList(request):
	if request.method=='GET':
		store=Store.objects.order_by('-id')
		keyword=request.GET.get('keyword',None)
		if keyword:
			store=Store.objects.filter(name__icontains=keyword)
		return render(request,'admin_view/store/store_list.html',{'stores':store,'keyword':keyword})




@permission_required('store.add_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeCreate(request):
	if request.method=='GET':
		locations=Location.objects.filter(parent=None)
		form=StoreForm()
		return render(request,'admin_view/store/add-store.html',{'form':form,'locations':locations})
	if request.method == 'POST':
		form = StoreForm(request.POST,request.FILES)
		locations=request.POST.getlist('locations',None)
		if form.is_valid():
			att=form.save(commit=True)
			for i in locations:
				loc=get_object_or_404(Location,id=i)
				att.location.add(loc)
			att.save()
			messages.success(
                            request, "Store has been added successfully.")
			return redirect('store:store-list')
		locations=Location.objects.filter(parent=None)
		return render(request,'admin_view/store/add-store.html',{'form':form,'locations':locations})


@permission_required('store.change_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateStore(request, pk):
	if request.method=='GET':
	    store = get_object_or_404(Store, pk=pk)
	    locations=Location.objects.filter(parent=None)
	    form = StoreForm(request.POST or None, instance=store)
	    return render(request, 'admin_view/store/update-store.html', {'form':form,'store':store,'locations':locations})
	if request.method=='POST':
		request_image = request.FILES.get('image',None)
		request_image_cleared = request.POST.get('image-clear')
		store = get_object_or_404(Store, pk=pk)
		form=StoreForm(request.POST,request.FILES,instance=store)
		locations=request.POST.getlist('locations',None)
		
		if form.is_valid():
			store.location.clear()
			att=form.save(commit=False)
			for i in locations:
				loc=get_object_or_404(Location,id=i)
				att.location.add(loc)

			if not request_image_cleared is None:
				att.image.delete(save=True)
			att.save()
			messages.success(request, "Store has been updated successfully.")
			return redirect('store:store-list')
		locations=Location.objects.filter(parent=None)
		return render(request, 'admin_view/store/update-store.html', {'form':form,'locations':locations,'store':store})

@permission_required('store.delete_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteStore(request,pk):
	get_object_or_404(Store, pk=pk).delete()
	store=request.POST.get('store-del',None)
	messages.success(request, "Store has been removed successfully.")
	if store=='store-del':
		return redirect('store:store-list')
	return redirect(request.META['HTTP_REFERER'])

@permission_required('store.delete_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteStoreBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            store=Store.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected store has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('store.change_store',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeAvailableStatus(request):
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		is_active=True if val == 'True' else False
		Store.objects.filter(id=item).update(is_active=is_active)
		return JsonResponse({'message':'Store has been updated.'})



@permission_required('store.view_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locationsList(request):
	if request.method=='GET':
		locations=Location.objects.order_by('-id')
		form=LocationForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			locations=Location.objects.filter(name__icontains=keywords)
		paginator = Paginator(locations, 20)
		try:
		   page = request.GET.get('page')
		   locations = paginator.get_page(page)
		except PageNotAnInteger:
		   locations = paginator.get_page(1)
		except EmptyPage:
		   locations = paginator.get_page(paginator.num_pages)
		return render(request,'admin_view/store/locations.html',{'locations':locations,'keywords':keywords,'form':form})

@permission_required('store.add_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locationsAjaxCreate(request):
    if request.method == 'POST':
    	form = LocationForm(request.POST)
    	if form.is_valid():
    		form.save()
    		messages.success(request, "Location has been Added Successfully")
    		return JsonResponse({'status': 'success'})
    	return JsonResponse({'errors': form.errors})



@permission_required('store.change_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locationsAjaxUpdate(request,pk):
	if request.method=='GET':
		locations=get_object_or_404(Location,id=pk)
		return JsonResponse({'status':'success','addons':model_to_dict(locations)})

	if request.method == 'POST':
		locations= get_object_or_404(Location,id=pk)
		form=LocationForm(request.POST,instance=locations)
		
		if form.is_valid():
			form.save()
			messages.success(
		                    request, "Locations has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

@permission_required('store.delete_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteLocationsBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            locations=Location.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected locations has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('store.delete_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locationsDelete(request,pk):
	if request.method=='POST':
		locations=get_object_or_404(Location,id=pk).delete()
		messages.success(request, "Location has been removed successfully.")
		return redirect('store:locations-list')

@permission_required('store.change_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locAvailableStatus(request):
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		if val == 'True':
			is_available=True
		if val == 'False':
			is_available=False
		Location.objects.filter(id=item).update(is_active=is_available)
		return JsonResponse({'message':'Location has been updated.'})


# @permission_required('store.view_sublocation',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
# def subLocationsList(request,loc):
# 	if request.method=='GET':
# 		main_loc=get_object_or_404(Location,id=loc)
# 		locations=SubLocation.objects.filter(location_id=loc).order_by('-id')
# 		form=SubLocationForm()
# 		keywords=request.GET.get('keywords',None)
# 		if keywords:
# 			locations=SubLocation.objects.filter(location_id=loc,name__icontains=keywords)
# 		return render(request,'admin_view/store/sub-location.html',{'locations':locations,'main_loc':main_loc,'keywords':keywords,'form':form,'loc':loc})

# @permission_required('store.add_sublocation',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
# def subLocationsAjaxCreate(request,loc):
#     if request.method == 'POST':
#     	form = SubLocationForm(request.POST)
#     	if form.is_valid():
#     		att=form.save(commit=False)
#     		att.location=get_object_or_404(Location,id=loc)
#     		att.save()
#     		messages.success(request, "Location has been Added Successfully")
#     		return JsonResponse({'status': 'success'})
#     	return JsonResponse({'errors': form.errors})



# @permission_required('store.change_sublocation',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
# def subLocationsAjaxUpdate(request,loc,pk):
# 	if request.method=='GET':
# 		locations=get_object_or_404(SubLocation,id=pk)
# 		return JsonResponse({'status':'success','addons':model_to_dict(locations)})

# 	if request.method == 'POST':
# 		locations= get_object_or_404(SubLocation,id=pk)
# 		form=SubLocationForm(request.POST,instance=locations)
		
# 		if form.is_valid():
# 			att=form.save(commit=False)
# 			att.location=get_object_or_404(Location,id=loc)
# 			att.save()
# 			messages.success(
# 		                    request, "Locations has been update Successfully")
# 			return JsonResponse({'status': 'success'})
# 		return JsonResponse({'errors': form.errors})

# @permission_required('store.delete_sublocation',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
# def deletesubLocationsBulk(request,loc):
#     if request.method=='POST':
#         item_id=request.POST.getlist('foo',None)
#         for i in range(0,len(item_id)):
#             locations=SubLocation.objects.filter(id=item_id[int(i)]).delete()
#         messages.success(request, "Selected locations has been removed successfully.")
#     return redirect(request.META['HTTP_REFERER'])

# @permission_required('store.delete_sublocation',raise_exception=True)
# @user_passes_test(lambda u: u.is_superuser or u.is_staff )
# def subLocationsDelete(request,loc,pk):
# 	if request.method=='POST':
# 		locations=get_object_or_404(SubLocation,id=pk).delete()
# 		messages.success(request, "Location has been removed successfully.")
# 		return redirect(request.META['HTTP_REFERER'])


