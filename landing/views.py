from django.shortcuts import render
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from .forms import *
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.db.models import Q
# from django.contrib.auth.decorators import permission_required
# from django.contrib.auth.mixins import PermissionRequiredMixin
from accounts.views import custom_permission_required as permission_required,SuperUserCheck


@permission_required('landing.view_location',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def locationList(request):
	if request.method == 'GET':
		next_url=request.GET.get('next_url',None)
		next_url='landing:'+str(next_url)
		location=Location.objects.filter(parent=None)
		return render(request, 'admin_view/landing/location_list.html', {'location': location,'next_url':next_url})



@permission_required(['landing.view_sectionone','landing.add_sectionone','landing.change_sectionone','landing.delete_sectionone'],raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def landing_section_one(request,slug):
	location=get_object_or_404(Location,slug=slug)
	obj = SectionOne.objects.filter(location__slug=location.slug).last()

	if request.method == 'GET':
		form = SectionOneForm(request.POST or None, instance=obj) if obj else SectionOneForm
		return render(request, 'admin_view/landing/section_one.html', {'form': form, 'obj': obj,'location':location})

	if request.method == 'POST':
		form = SectionOneForm(request.POST, request.FILES, instance=obj) if obj else SectionOneForm(request.POST, request.FILES)
		result =  SectionOne.update_section_1(request,form,location) if obj else SectionOne.create_section_1(request,form,location)
		messages.success(request, result)
		return redirect(request.META['HTTP_REFERER'])



"""Landing page category section crud"""

@permission_required('landing.view_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryList(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		category=LandingCategories.objects.filter(location__slug=location.slug).order_by('-id')
		form=LandingCategoriesForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			category=LandingCategories.objects.filter(Q(category__name__icontains=keywords) & Q(location__slug=location.slug))
		return render(request,'admin_view/landing/landingCategory.html',{'category':category,'keywords':keywords,'form':form,'location':location})

@permission_required('landing.add_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryCreate(request,slug):
    if request.method == "GET":
    	location=get_object_or_404(Location,slug=slug)
    	form= LandingCategoriesForm()
    	choose_category=Category.objects.all()
    	return render(request,'admin_view/landing/landingCategoryCreate.html',{'form':form,'choose_category':choose_category,'location':location})
    if request.method == 'POST':
    	form = LandingCategoriesForm(request.POST,request.FILES)
    	location=get_object_or_404(Location,slug=slug)
    	if form.is_valid():
    		att=form.save(commit=False)
    		att.location=location
    		att.save()
    		messages.success(
		                    request, "Category has been Added Successfully")
    		return redirect('landing:category-list',slug=location.slug)
    	choose_category=Category.objects.all()
    	return render(request,'admin_view/landing/landingCategoryCreate.html',{'form':form,'choose_category':choose_category,'location':location})




@permission_required('landing.change_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryUpdate(request,pk,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		choose_category=Category.objects.all()
		category=get_object_or_404(LandingCategories,id=pk)
		form=LandingCategoriesForm(instance=category)
		return render(request,'admin_view/landing/landingCategoryUpdate.html',{'form':form,'choose_category':choose_category,'category':category,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		category= get_object_or_404(LandingCategories,id=pk)
		form=LandingCategoriesForm(request.POST,request.FILES,instance=category)
		if form.is_valid():
			att=form.save(commit=False)
			att.location=location
			att.save()
			messages.success(
		                    request, "Category has been Added Successfully")
			return redirect('landing:category-list',slug=location.slug)
		choose_category=Category.objects.all()
		return render(request,'admin_view/landing/landingCategoryUpdate.html',{'form':form,'choose_category':choose_category,'category':category,'location':location})

@permission_required('landing.delete_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteCategoryBulk(request,slug):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            locations=LandingCategories.objects.filter(id=item_id[int(i)],location__slug=slug).delete()
        messages.success(request, "Selected categories has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.delete_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryDelete(request,pk,slug):
	if request.method=='POST':
		location=get_object_or_404(Location,slug=slug)
		category=get_object_or_404(LandingCategories,id=pk,location__slug=slug).delete()
		messages.success(request, "Category has been removed successfully.")
		return redirect('landing:category-list',slug=location.slug)

@permission_required('landing.change_landingcategories',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryActiveUpdate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		LandingCategories.updateActiveStatus(location,val,item)
		return JsonResponse({'message':'Category has been updated.'})

""" Best seller product section crud"""
@permission_required('landing.view_bestsellerssection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productList(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		product=BestSellersSection.objects.filter(location__slug=location.slug).order_by('-id')
		choose_product=Product.objects.filter(store__location=location)
		form=BestSellersSectionForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			product=BestSellersSection.objects.filter(Q(product__name__icontains=keywords) & Q(location__slug=location.slug))
		return render(request,'admin_view/landing/landingBestSeller.html',{'product':product,'keywords':keywords,'form':form,'choose_product':choose_product,'location':location})

@permission_required('landing.add_bestsellerssection',raise_exception=True)#
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productCreate(request,slug):
	if request.method == "GET":
		location=get_object_or_404(Location,slug=slug)
		form= BestSellersSectionForm()
		choose_product=Product.objects.filter(store__location=location)
		return render(request,'admin_view/landing/landingBestSellerCreate.html',{'form':form,'choose_product':choose_product,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		form = BestSellersSectionForm(request.POST)
		product=request.POST.get('product',None)
		if form.is_valid():
			att=form.save(commit=False)
			att.location=location
			att.save()
			messages.success(
		                    request, "Product has been Added Successfully")
			return redirect('landing:product-list',slug=location.slug)
		choose_product=Product.objects.filter(store__location=location)
		return render(request,'admin_view/landing/landingBestSellerCreate.html',{'form':form,'choose_product':choose_product,'location':location})



@permission_required('landing.change_bestsellerssection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productUpdate(request,pk,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		choose_product=Product.objects.filter(store__location=location)
		product=get_object_or_404(BestSellersSection,id=pk)
		form=BestSellersSectionForm(instance=product)
		return render(request,'admin_view/landing/landingBestSellerUpdate.html',{'form':form,'choose_product':choose_product,'product':product,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		product= get_object_or_404(BestSellersSection,id=pk)
		form=BestSellersSectionForm(request.POST,instance=product)
		if form.is_valid():
			att=form.save(commit=False)
			att.location=location
			att.save()
			messages.success(
		                    request, "Product has been Added Successfully")
			return redirect('landing:product-list', slug=location.slug)
		choose_product=Product.objects.filter(store__location=location)
		return render(request,'admin_view/landing/landingBestSellerUpdate.html',{'form':form,'choose_product':choose_product,'product':product,'location':location})

@permission_required('landing.delete_bestsellerssection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteProductBulk(request,slug):
    if request.method=='POST':
    	location=get_object_or_404(Location,slug=slug)
    	item_id=request.POST.getlist('foo',None)
    	for i in range(0,len(item_id)):
    		BestSellersSection.objects.filter(id=item_id[int(i)],location__slug=location.slug).delete()
    	messages.success(request, "Selected products has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.delete_bestsellerssection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productDelete(request,pk,slug):
	if request.method=='POST':
		location=get_object_or_404(Location,slug=slug)
		get_object_or_404(BestSellersSection,id=pk,location__slug=location.slug).delete()
		messages.success(request, "Product has been removed successfully.")
		return redirect('landing:product-list',slug=slug)

@permission_required('landing.chagne_bestsellerssection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productActiveUpdate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		BestSellersSection.updateActiveStatus(location,val,item)
		return JsonResponse({'message':'Category has been updated.'})

""" Explore store  section crud"""
@permission_required('landing.view_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeList(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		store=ExploreStore.objects.filter(location__slug=location.slug).order_by('-id')
		keywords=request.GET.get('keywords',None)
		if keywords:
			store=ExploreStore.objects.filter(Q(store__name__icontains=keywords) & Q(location__slug=location.slug))
		return render(request,'admin_view/landing/storeList.html',{'store':store,'keywords':keywords,'location':location})
	




@permission_required('landing.add_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeCreate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		form=ExploreStoreForm()
		choose_store=Store.objects.filter(location=location)
		return render(request,'admin_view/landing/storeCreate.html',{'choose_store':choose_store,'form':form,'location':location})
	
	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		form = ExploreStoreForm(request.POST)
		if form.is_valid():
			att=form.save(commit=False)
			att.location=location
			att.save()
			messages.success(
                            request, "Store has been added successfully.")
			return redirect('landing:store-list',slug=location.slug)
		choose_store=Store.objects.filter(location=location)
		return render(request,'admin_view/landing/storeCreate.html',{'choose_store':choose_store,'form':form,'location':location})


@permission_required('landing.change_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateStore(request, pk,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		choose_store=Store.objects.filter(location=location)
		store=get_object_or_404(ExploreStore,id=pk)
		form=ExploreStoreForm(instance=store)
		return render(request,'admin_view/landing/storeUpdate.html',{'form':form,'choose_store':choose_store,'store':store,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		store= get_object_or_404(ExploreStore,id=pk,location__slug=location.slug)
		form=ExploreStoreForm(request.POST,instance=store)
		if form.is_valid():
			att=form.save(commit=False)
			att.location=location
			att.save()
			messages.success(
		                    request, "Store has been Added Successfully")
			return redirect('landing:store-list',slug=location.slug)
		choose_store=Store.objects.filter(location=location)
		return render(request,'admin_view/landing/storeUpdate.html',{'form':form,'choose_store':choose_store,'store':store,'location':location})

@permission_required('landing.delete_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteStore(request,pk,slug):
	location=get_object_or_404(Location,slug=slug)
	get_object_or_404(ExploreStore, pk=pk,location__slug=location.slug).delete()
	messages.success(request, "Store has been removed successfully.")
	return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.delete_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteStoreBulk(request,slug):
    if request.method=='POST':
    	location=get_object_or_404(Location,slug=slug)
    	item_id=request.POST.getlist('foo',None)
    	for i in range(0,len(item_id)):
    		ExploreStore.objects.filter(id=item_id[int(i)],location__slug=location.slug).delete()
    	messages.success(request, "Selected store has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.change_explorestore',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def storeActiveUpdate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		ExploreStore.updateActiveStatus(location,val,item)
		return JsonResponse({'message':'Store has been updated.'})



"""Landing page flavour section crud"""

@permission_required('landing.view_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourList(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		flavour=PopularFlavourSection.objects.filter(location__slug=location.slug).order_by('-id')
		form=PopularFlavourSectionForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			flavour=PopularFlavourSection.objects.filter(Q(flavour__name__icontains=keywords) & Q(location__slug=location.slug))
		return render(request,'admin_view/landing/flavourList.html',{'flavour':flavour,'keywords':keywords,'form':form,'location':location})

@permission_required('landing.add_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourCreate(request,slug):
    if request.method == "GET":
    	location=get_object_or_404(Location,slug=slug)
    	form= PopularFlavourSectionForm()
    	choose_flavour=Flavour.objects.all()
    	return render(request,'admin_view/landing/flavourCreate.html',{'form':form,'choose_flavour':choose_flavour,'location':location})
    if request.method == 'POST':
    	location=get_object_or_404(Location,slug=slug)
    	form = PopularFlavourSectionForm(request.POST,request.FILES)
    	if form.is_valid():
    		att=form.save(commit=False)
    		att.location=location
    		att.save()
    		messages.success(
		                    request, "Flavour has been Added Successfully")
    		return redirect('landing:flavour-list',slug=location.slug)
    	choose_flavour=Flavour.objects.all()
    	return render(request,'admin_view/landing/flavourCreate.html',{'form':form,'choose_flavour':choose_flavour})




@permission_required('landing.change_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourUpdate(request,pk,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		choose_flavour=Flavour.objects.all()
		flavour=get_object_or_404(PopularFlavourSection,id=pk)
		form=PopularFlavourSectionForm(instance=flavour)
		return render(request,'admin_view/landing/flavourUpdate.html',{'form':form,'choose_flavour':choose_flavour,'flavour':flavour,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		flavour= get_object_or_404(PopularFlavourSection,id=pk)
		form=PopularFlavourSectionForm(request.POST,request.FILES,instance=flavour)
		if form.is_valid():
			att=form.save(commit=False)
			att.save()
			messages.success(
		                    request, "Flavour has been Added Successfully")
			return redirect('landing:flavour-list',slug=location.slug)
		choose_flavour=Flavour.objects.all()
		return render(request,'admin_view/landing/flavourUpdate.html',{'form':form,'choose_flavour':choose_flavour,'flavour':flavour,'location':location})

@permission_required('landing.delete_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteFlavourBulk(request,slug):
    if request.method=='POST':
    	location=get_object_or_404(Location,slug=slug)
    	item_id=request.POST.getlist('foo',None)
    	for i in range(0,len(item_id)):
    		PopularFlavourSection.objects.filter(id=item_id[int(i)],location__slug=location.slug).delete()
    	messages.success(request, "Selected flavours has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.delete_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourDelete(request,pk,slug):
	if request.method=='POST':
		location=get_object_or_404(Location,slug=slug)
		get_object_or_404(PopularFlavourSection,id=pk,location__slug=location.slug).delete()
		messages.success(request, "Flavour has been removed successfully.")
		return redirect('landing:flavour-list',slug=location.slug)


@permission_required('landing.change_popularflavoursection',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourActiveUpdate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		PopularFlavourSection.updateActiveStatus(location,val,item)
		return JsonResponse({'message':'Flavour has been updated.'})





"""Landing page banner section crud"""

@permission_required('landing.view_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def bannerList(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		banner=LandingFullBanner.objects.filter(location__slug=location.slug).order_by('-id')
		form=LandingFullBannerForm()
		return render(request,'admin_view/landing/bannerList.html',{'banner':banner,'form':form,'location':location})

@permission_required('landing.add_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def bannerCreate(request,slug):
    if request.method == "GET":
    	location=get_object_or_404(Location,slug=slug)
    	form= LandingFullBannerForm()
    	return render(request,'admin_view/landing/bannerCreate.html',{'form':form,'location':location})
    if request.method == 'POST':
    	location=get_object_or_404(Location,slug=slug)
    	form = LandingFullBannerForm(request.POST,request.FILES)
    	image=request.FILES.get('image',None)
    	if form.is_valid():
    		att=form.save(commit=False)
    		att.image=image
    		att.location=location
    		att.save()
    		messages.success(
		                    request, "Banner has been Added Successfully")
    		return redirect('landing:banner-list',slug=location.slug)
    	return render(request,'admin_view/landing/bannerCreate.html',{'form':form,'location':location})




@permission_required('landing.update_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def bannerUpdate(request,pk,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		banner=get_object_or_404(LandingFullBanner,id=pk)
		form=LandingFullBannerForm(instance=banner)
		return render(request,'admin_view/landing/bannerUpdate.html',{'form':form,'banner':banner,'location':location})

	if request.method == 'POST':
		location=get_object_or_404(Location,slug=slug)
		banner= get_object_or_404(LandingFullBanner,id=pk)
		form=LandingFullBannerForm(request.POST,request.FILES,instance=banner)
		image=request.FILES.get('image',None)
		if form.is_valid():
			att=form.save(commit=False)
			att.image=image
			att.location=location
			att.save()
			messages.success(
		                    request, "Banner has been Added Successfully")
			return redirect('landing:banner-list',slug=location.slug)
		return render(request,'admin_view/landing/bannerUpdate.html',{'form':form,'banner':banner})

@permission_required('landing.delete_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteBannerBulk(request,slug):
    if request.method=='POST':
    	location=get_object_or_404(Location,slug=slug)
    	item_id=request.POST.getlist('foo',None)
    	for i in range(0,len(item_id)):
    		LandingFullBanner.objects.filter(id=item_id[int(i)],location__slug=location.slug).delete()
    	messages.success(request, "Selected banner has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('landing.delete_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def bannerDelete(request,pk,slug):
	if request.method=='POST':
		location=get_object_or_404(Location,slug=slug)
		get_object_or_404(LandingFullBanner,id=pk,location__slug=location.slug).delete()
		messages.success(request, "Banner has been removed successfully.")
		return redirect('landing:banner-list',slug=location.slug)


@permission_required('landing.change_landingfullbanner',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def bannerActiveUpdate(request,slug):
	if request.method=='GET':
		location=get_object_or_404(Location,slug=slug)
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		LandingFullBanner.updateActiveStatus(location,val,item)
		return JsonResponse({'message':'Banner has been updated.'})
