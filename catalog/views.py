from django.views.generic import ListView,DetailView
from catalog.models import *
from django.shortcuts import render, redirect, get_object_or_404
from catalog.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse,Http404,JsonResponse
import os
from django.db.models import Q
from django.conf import settings
import requests
from mimetypes import guess_type
import json
from django.http import HttpResponse
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models.fields.files import ImageFieldFile
from django.urls import reverse
from django.http import JsonResponse
from accounts.views import custom_permission_required as permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def download(request):
	file_path=os.path.join('static', 'ordersathi-store.xlsx')
	with open(file_path, 'rb') as f:
		response = HttpResponse(f, content_type=guess_type(file_path)[0])
		response['Content-Length'] = len(response.content)
		response['Content-Disposition'] = 'attachment; filename=ordersathi-store.xlsx'
		return response

@permission_required('catalog.view_category',raise_exception=True) 
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def categoryList(request):
	"""Listing category, catalog-->>category"""
	if request.method=='GET':
		category=Category.objects.order_by('-id')
		category_keyword=request.GET.get('category_keyword',None)
		if category_keyword:
			category=category.filter(name__icontains=category_keyword)
		return render(request,'admin_view/catalog/categories.html',{'category':category,'category_keyword':category_keyword})

@user_passes_test(lambda u: u.is_superuser)
def ajaxCategoryCreate(request):
	"""Currently not used, ajax create category."""
    
	if request.method == 'POST':
		form = CategoryForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(
	                        request, "Category Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

@permission_required('catalog.add_category',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def CategoryCreate(request):
	"""Creating categories"""
	if request.method=='GET':
		form=CategoryForm()
		return render(request,'admin_view/catalog/add-category.html',{'form':form})
	if request.method == 'POST':
		form = CategoryForm(request.POST,request.FILES)
		is_active=request.POST['radioInline']
		if form.is_valid():
			attachment=form.save(commit=False)
			if is_active=='True':
				attachment.is_available=True
			attachment.save()
			messages.success(request, "Category has been added successfully.")
			return redirect('catalog:category')
		return render(request,'admin_view/catalog/add-category.html',{'form':form})


@permission_required('catalog.change_category',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateCategory(request, pk):
	"""Updating Categories"""
	if request.method =='GET':
	    category = get_object_or_404(Category, pk=pk)
	    form = CategoryForm(instance=category)
	    return render(request, 'admin_view/catalog/update-category.html', {'form':form,'category':category})
	    
	if request.method=='POST':
		category = get_object_or_404(Category, pk=pk)
		form = CategoryForm(request.POST,request.FILES,instance=category)
		is_active=request.POST.get('radioInline',None)
		if form.is_valid():
			attachment=form.save(commit=True)
			if is_active=='True':
				attachment.is_available=True
			attachment.save()
			messages.success(request, "Category has been updated successfully.")
			return redirect('catalog:category')
		return render(request, 'admin_view/catalog/update-category.html', {'form':form,'category':category})

@permission_required('catalog.delete_category',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteCategory(request,pk):
	"""Deleting particular category"""
	category = get_object_or_404(Category, pk=pk).delete()
	cat=request.POST.get('category-del',None)
	messages.success(request, "Category has been removed successfully.")
	if cat=='category-del':
		return redirect('catalog:category')
	return redirect(request.META['HTTP_REFERER'])

@permission_required('catalog.delete_category',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteCategoryBulk(request):
	"""Deleting category in bulk"""
	if request.method=='POST':
	    item_id=request.POST.getlist('foo',None)
	    for i in range(0,len(item_id)):
	        category=Category.objects.filter(id=item_id[int(i)]).delete()
	    messages.success(request, "Selected Categories has been removed successfully.")
	return redirect(request.META['HTTP_REFERER'])





@permission_required('catalog.view_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def productList(request,slug):
	"""Product list catalog-->store-->products"""
	if request.method=='GET':
		store=get_object_or_404(Store,slug=slug)
		form=ProductVarientForm()
		category=Category.objects.filter(category__in=Product.objects.all()).distinct()
		product=Product.objects.filter(store__slug=slug).order_by('-id')
		category1=request.GET.getlist('category',None)
		keywords=request.GET.get('product_keyword',None)
		if keywords:
			product=Product.objects.filter(Q(Q(name__icontains=keywords) | Q(product__product_code__icontains=keywords)| Q(category__name__icontains=keywords)) & Q(store__slug=slug)).distinct()
		if category1:
			product=Product.objects.filter(Q(category__name__in=category1) & Q(store__slug=slug)).distinct()
		if keywords and category1:
			product=Product.objects.filter(Q(Q(name__icontains=keywords) | Q(product__product_code__icontains=keywords)| Q(category__name__icontains=keywords)|Q(category__name__in=category1)) & Q(store__slug=slug)).distinct()
		try:
			p = Paginator(product, 50)
		except:
			p = Paginator(product, 50)
		page_number = request.GET.get('page')
		if page_number is None:
			page_number = 1
		try:
			page_obj = p.get_page(page_number)
		except PageNotAnInteger:
			page_obj = p.page(1)
		except EmptyPage:
			page_obj = p.page(p.num_pages)
		return render(request,'admin_view/catalog/products.html',{'product':page_obj,'category':category,'keywords':keywords,'category1':category1,'form':form,'store__slug':slug,'store':store, 'page_number':int(page_number)})

	

from settings.models import ShippingMethod
import pdb
@permission_required('catalog.add_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def ProductCreate(request,slug):
	"""Creating products"""
	if request.method=='GET':
		store=get_object_or_404(Store,slug=slug)
		attributes = Attribute.objects.all()
		form=ProductForm()	
		form1 = ProductVarientForm()
		products_to_relate=Product.objects.filter(store__slug=slug)
		attr_value = ProductAttributeValueForm()
		return render(request,'admin_view/catalog/add-product.html',{'form':form,'form1':form1,'attributes':attributes,'store__slug':slug,'store':store,})

	if request.method == 'POST':
		store=get_object_or_404(Store,slug=slug)
		products_to_relate=Product.objects.filter(store__slug=slug)
		abc = request.POST.get('alka',None)
		if abc:
			return JsonResponse({'form':ProductVarientForm().as_p()})
		form = ProductForm(request.POST,request.FILES)
		if form.is_valid():
			product=form.save()
			product.store=store
			product.save()	
			try:
				forms = [
					ProductVarientForm(dict(old_price=op, price=p,cost_price=cp, product_code=pc,quantity=q,
					attribute_name_1=n1,attribute_value_1=v1,attribute_name_2=n2,attribute_value_2=v2,display_order_varient=dov))
					for op, p, cp, pc,q,n1,v1,n2,v2,dov in zip(
							request.POST.getlist("old_price"),
							request.POST.getlist("price"),
       					request.POST.getlist("cost_price"),
							request.POST.getlist("product_code"),
							request.POST.getlist("quantity"),
							request.POST.getlist("attribute_name_1"),
							request.POST.getlist("attribute_value_1"),
							request.POST.getlist("attribute_name_2"),
							request.POST.getlist("attribute_value_2"),
       					request.POST.getlist("display_order_varient"),
							
					)
				]
			
				for i in range(len(forms)):
					if forms[i].is_valid():
						for form_count,form in enumerate(forms):
							_form = form.save(commit=False)
							_varient_name = str(product.name) + "-" + str(form['attribute_value_1'].value())+ "-" + str(form['attribute_value_2'].value())
							_form.product = product
							_form.varient_name = _varient_name
							_form.is_available_varient = True
							_form.status = True
							_form.save()
							attr_name_1 = form['attribute_name_1'].value()
							attr_value_1 = form['attribute_value_1'].value()
							attr_name_2 = form['attribute_name_2'].value()
							attr_value_2 = form['attribute_value_2'].value()
							if attr_name_1 and attr_value_1:
								attribute = Attribute.objects.get(name=attr_name_1)
								attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_1)
								_form.attribut_value.add(attr_value_obj)
							if attr_name_2 and attr_value_2:
								attribute = Attribute.objects.get(name=attr_name_2)
								attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_2)
								_form.attribut_value.add(attr_value_obj)
					else:
						continue
						print("invalid")
				messages.success(request, "Product has been added successfully.")
				return redirect('catalog:product',slug=slug)
			except Exception as e:
				print(e,"===")
			messages.success(request, "Product has been added successfully.")
			return redirect('catalog:product',slug=slug)				
		else:
			attributes = Attribute.objects.all()
			return render(request,'admin_view/catalog/add-product.html',{'form':form,'store__slug':slug,'attributes':attributes})


@user_passes_test(lambda u: u.is_superuser)
def ajaxProductCreate(request):
	"""Not used currently"""
	if request.method == 'POST':
		form = ProductForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, " Product Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

from django.db.models import ProtectedError
@permission_required('catalog.delete_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteProduct(request,pk,slug):
	"""Deleting particular product"""
	try:
		product = get_object_or_404(Product, pk=pk,store__slug=slug).delete()
		messages.success(request, "Product has been removed successfully.")
	except ProtectedError as e:
		messages.error(request, 'Cannot delete some instances of model because varient are related to Orders. So first delete related Order to delete this product.')
	return redirect('catalog:product',slug=slug)

@permission_required('catalog.delete_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteProductBulk(request):
	"""Deleting products in bulk"""
	if request.method=='POST':
	    item_id=request.POST.getlist('foo',None)
	    for i in range(0,len(item_id)):
	    	try:
	    		product=Product.objects.filter(id=item_id[int(i)]).delete()
	    		messages.success(request, "Selected products has been removed successfully.")
	    	except ProtectedError:
	    		messages.error(request, 'Cannot delete some instances of model because varient are related to Orders. So first delete related Order to delete this product.')
	    return redirect(request.META['HTTP_REFERER'])



@permission_required('catalog.change_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateProduct(request, pk,slug):
	"""Updating product"""
	if request.method == "GET":
		product = get_object_or_404(Product, pk=pk,store__slug=slug)
		form = ProductForm(instance=product)
		varients = ProductVarient.objects.filter(product=product,product__store__slug=slug,base_varient=False,status=True).order_by('display_order_varient')
		base_varients = ProductVarient.objects.filter(product=product,product__store__slug=slug,base_varient=True,status=True).order_by('display_order_varient').last()
		attributes = Attribute.objects.all()
		try:
			for item  in varients:
				if item.attribut_value.filter(attribute__name='Weight').exists():
					first_attr_names='Weight'
				elif item.attribut_value.filter(attribute__name='Quantity').exists():
					first_attr_names='Quantity'
				else:
					first_attr_names=False		
			if first_attr_names:
				first_attr_value = list(set([item.attribut_value.get(attribute__name=first_attr_names).value for item  in varients]))
			else:
				first_attr_value=[]
		except:
			first_attr_names=False
			first_attr_value = []
		
		try:
			for item  in varients:
				if item.attribut_value.filter(attribute__name='Flavour').exists():
					second_attr_names='Flavour'
				else:
					second_attr_names=False#varients[0].attribut_value.all()[1].attribute.name
			if second_attr_names:
				second_attr_value = list(set([item.attribut_value.get(attribute__name=second_attr_names).value for item  in varients]))
			else:
				second_attr_value=[]
		except:
			second_attr_names=False
			second_attr_value = []
		all_varient_sku = [item.product_code for item in varients]
		return render(request, 'admin_view/catalog/update-product.html', {'form':form,'varients':varients,'base_varients':base_varients,'product':product,
		'attributes':attributes,'first_attr_value':first_attr_value,'second_attr_value':second_attr_value,'all_varient_sku':all_varient_sku,'store__slug':slug,'first_attr_names':first_attr_names,
		'second_attr_names':second_attr_names})

	if request.method == "POST":
		store=get_object_or_404(Store,slug=slug)
		product = get_object_or_404(Product, pk=pk,store__slug=slug)
		form = ProductForm(request.POST,request.FILES ,instance=product)

		if form.is_valid(): 
			product_form = form.save()
			product_form.store=store	
			product_form.save()
			try:
				forms = [
					ProductVarientForm(dict(old_price=op, price=p,cost_price=cp, product_code=pc,quantity=q,
					attribute_name_1=n1,attribute_value_1=v1,attribute_name_2=n2,attribute_value_2=v2,display_order_varient=dov))
					for op, p,cp, pc,q,n1,v1,n2,v2,dov in zip(
							request.POST.getlist("old_price"),
							request.POST.getlist("price"),
	   					request.POST.getlist("cost_price"),
							request.POST.getlist("product_code"),
							request.POST.getlist("quantity"),
							request.POST.getlist("attribute_name_1"),
							request.POST.getlist("attribute_value_1"),
							request.POST.getlist("attribute_name_2"),
							request.POST.getlist("attribute_value_2"),
	   					request.POST.getlist("display_order_varient"),
							
					)
				]
				varient_id_list = request.POST.getlist("varient_id")
				all_products_varients_id = [str(item.id) for item in Product.objects.get(id=product.id).product.all()]
				ProductVarient.remove_varient_edit(varient_id_list,all_products_varients_id)
				
				for count,form in enumerate(forms):
					if form.is_valid():
						try:
							varient_id = int(varient_id_list[count])
						except:
							varient_id = None

						if (not varient_id is None) and (ProductVarient.objects.filter(id__in=varient_id_list).exists()):
							_varient_name = str(product.name) + "-" + str(form['attribute_value_1'].value())+ "-" + str(form['attribute_value_2'].value())
							pv = ProductVarient.objects.get(id=varient_id)
							pv.varient_name = _varient_name
							pv.old_price = form.cleaned_data['old_price']
							pv.cost_price = form.cleaned_data['cost_price']
							pv.price = form.cleaned_data['price']
							pv.display_order_varient = form.cleaned_data['display_order_varient']
							pv.product_code = form.cleaned_data['product_code']
							pv.quantity = form.cleaned_data['quantity']
							pv.is_available_varient = form.cleaned_data['is_available_varient']
							pv.status=True
							pv.save()

							attr_name_1 = form['attribute_name_1'].value()
							attr_value_1 = form['attribute_value_1'].value()
							attr_name_2 = form['attribute_name_2'].value()
							attr_value_2 = form['attribute_value_2'].value()
							pv.attribut_value.clear()
				
							if attr_name_1 and attr_value_1:
								try:
									attribute = Attribute.objects.get(name=attr_name_1)
									attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_1)
									pv.attribut_value.add(attr_value_obj)
								except:
									pass
							
							if attr_name_2 and attr_value_2:
								try:
									attribute = Attribute.objects.get(name=attr_name_2)
									attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_2)
									pv.attribut_value.add(attr_value_obj)
								except:
									pass

						else:
							_form = form.save(commit=False)
							_varient_name = str(product.name) + "-" + str(form['attribute_value_1'].value())+ "-" + str(form['attribute_value_2'].value())
							_form.product = product
							_form.varient_name = _varient_name
							_form.is_available_varient = True
							_form.status = True
							_form.save()

							attr_name_1 = form['attribute_name_1'].value()
							attr_value_1 = form['attribute_value_1'].value()
							attr_name_2 = form['attribute_name_2'].value()
							attr_value_2 = form['attribute_value_2'].value()

							if attr_name_1 and attr_value_1:
								try:
									attribute = Attribute.objects.get(name=attr_name_1)
									attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_1)
									_form.attribut_value.through.objects.get_or_create(attributevalue_id=attr_value_obj.id,productvarient_id=_form.id)
								except:
									pass
							if attr_name_2 and attr_value_2:
								try:
									attribute = Attribute.objects.get(name=attr_name_2)
									attr_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attr_value_2)
									_form.attribut_value.through.objects.get_or_create(attributevalue_id=attr_value_obj.id,productvarient_id=_form.id)
								except:
									pass
							
					else:
						print("invalid")	
				messages.success(request, "Product has been added successfully.")
				return redirect('catalog:product',slug=slug)
			except Exception as e:
				print(e,"===")
		messages.error(request, "Unable to update.")
		return redirect('catalog:product',slug=slug)

			
		

from pyexcel_xlsx import get_data
import json
import ast
@user_passes_test(lambda u: u.is_superuser,lambda u: u.is_staff)
def excelUpload(request):
	"""upload excel sheet of product to add product.
	 Currently not used and need to modify code based on sheet"""
	if request.method=='POST':
		form=FileUploadForm(request.POST,request.FILES)
		if form.is_valid():
			filehandle = request.FILES['file']
			data=get_data(filehandle)
			data=json.dumps(data)
			data=ast.literal_eval(data)
			product=data['Product']
			varient=data['Varient']
			for i in range(1,len(product)):
					category=product[i][2].lower()
					category=category.strip()
					category=Category.objects.get_or_create(display_order=1,name=category)
					
					tag=product[i][6].lower()
					tag=tag.strip()
					
					tag=Tags.objects.get_or_create(name=tag)

					product_name=product[i][0].lower()
					product_name=product_name.strip()
					is_available=product[i][3].lower()
					is_featured = product[i][4].lower()
					is_new = product[i][5].lower()

					is_available=is_available.strip()
					is_featured = is_featured.strip()
					is_new = is_new.strip()
					if is_available =='yes':
						is_available=True
					else:
						is_available=False

					if is_featured =='yes':
						is_featured=True
					else:
						is_featured=False

					if is_new =='yes':
						is_new=True
					else:
						is_new=False


					product1=Product.objects.get_or_create(name=product_name,
						description=product[i][1],
						tags=tag[0],
						is_available=is_available,
						display_order=product[i][7],
						is_new = is_new,
						is_recomended= is_featured
						)
					
					product_id=product1[0].id
					product1[0].category.through.objects.get_or_create(category_id=category[0].id,product_id=product_id)

				
			for i in range(1,len(varient)):
				try:
					base_varient=varient[i][7].lower()
					base_varient=base_varient.strip()
					base_varient=Product.objects.get(name=base_varient)
					varient_name=varient[i][0].lower()
					varient_name=varient_name.strip()
					is_available=varient[i][5].lower()
					is_available=is_available.strip()
					sku=varient[i][1]
					sku=sku

					
					
					discounted_price=varient[i][3]
					if not discounted_price:
						discounted_price=None
					
					if is_available =='yes':
						is_available=True
					else:
						is_available=False
					
					varient_obj,created = ProductVarient.objects.get_or_create(varient_name=varient_name,
						product=base_varient,
						product_code=sku,
						quantity=varient[i][4],
						is_available_varient=is_available,
						display_order_varient=varient[i][6],
						old_price=varient[i][2],
						price=discounted_price,
						)
					attribute_name_1 = varient[i][8].title()
					attribute_value_1 = varient[i][9].title()
					
					attribute_name_2 = varient[i][10].title()
					attribute_value_2 = varient[i][11].title()

					if attribute_name_1 and attribute_value_1:
						attribute,created = Attribute.objects.get_or_create(name=attribute_name_1)
						attribute_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attribute_value_1)
						varient_id=varient_obj.id
						varient_obj.attribut_value.through.objects.get_or_create(attributevalue_id=attribute_value_obj.id,productvarient_id=varient_id)
					
					if attribute_name_2 and attribute_value_2:
						attribute,created = Attribute.objects.get_or_create(name=attribute_name_2)
						attribute_value_obj,created = AttributeValue.objects.get_or_create(attribute=attribute,value=attribute_value_2)
						varient_id=varient_obj.id
						varient_obj.attribut_value.through.objects.get_or_create(attributevalue_id=attribute_value_obj.id,productvarient_id=varient_id)
					
				except Exception as e:
					pass

		messages.success(request, "Product were successfully added.")
		return redirect('catalog:product')

				
@permission_required('catalog.change_category',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def catAvailableStatus(request):
	"""Updating category availability status via ajax"""
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		if val == 'True':
			is_available=True
		if val == 'False':
			is_available=False
		Category.objects.filter(id=item).update(is_available=is_available)
		return JsonResponse({'message':'Category has been updated.'})

@permission_required('catalog.change_product',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def proAvailableStatus(request):
	"""Updating product availability status via ajax"""
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		if val == 'True':
			is_available=True
		if val == 'False':
			is_available=False
		Product.objects.filter(id=item).update(is_available=is_available)
		return JsonResponse({'message':'Product has been updated.'})





@permission_required('catalog.view_tags',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def tagsList(request):
	"""Tags listing"""
	if request.method=='GET':
		tags=Tags.objects.order_by('-id')
		form=TagForm()
		keywords=request.GET.get('keywords',None)

		if keywords:
			tags=Tags.objects.filter(Q(name__icontains=keywords))
		return render(request,'admin_view/catalog/tags.html',{'tags':tags,'keywords':keywords,'form':form})

@permission_required('catalog.add_tags',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def tagsAjaxCreate(request):
	"""creating tags"""
	if request.method == 'POST':
		form = TagForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(
		                    request, "Tags has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})



@permission_required('catalog.change_tags',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def tagAjaxUpdate(request,pk):
	"""Updating tags"""
	if request.method=='GET':
		tags=get_object_or_404(Tags,id=pk)
		return JsonResponse({'status':'success','addons':model_to_dict(tags)})

	if request.method == 'POST':
		tags= get_object_or_404(Tags,id=pk)
		form=TagForm(request.POST,instance=tags)
		if form.is_valid():
			form.save()
			messages.success(
		                    request, "Addon has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

@permission_required('catalog.delete_tags',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteTagsBulk(request):
	"""deleting tags in bulk"""
	if request.method=='POST':
	    item_id=request.POST.getlist('foo',None)
	    for i in range(0,len(item_id)):
	        tags=Tags.objects.filter(id=item_id[int(i)]).delete()
	    messages.success(request, "Selected tags has been removed successfully.")
	return redirect(request.META['HTTP_REFERER'])

@permission_required('catalog.delete_tags',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def tagsDelete(request,pk):
	"""Deleting particular tags"""
	if request.method=='POST':
		tags=get_object_or_404(Tags,id=pk).delete()
		messages.success(request, "Tags has been removed successfully.")
		return redirect('catalog:tags-list')



@permission_required('catalog.view_attribute',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def attributeList(request):
	if request.method=='GET':
		attribute=Attribute.objects.order_by('-id')
		form=AttributeForm()
		keywords=request.GET.get('keywords',None)

		if keywords:
			attribute=Attribute.objects.filter(Q(name__icontains=keywords))
		return render(request,'admin_view/catalog/attribute.html',{'attribute':attribute,'keywords':keywords,'form':form})

@permission_required('catalog.add_attribute',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def attributeAjaxCreate(request):
    if request.method == 'POST':
    	form = AttributeForm(request.POST)
    	if form.is_valid():
    		form.save()
    		messages.success(
		                    request, "Attribute has been Added Successfully")
    		return JsonResponse({'status': 'success'})
    	return JsonResponse({'errors': form.errors})



@permission_required('catalog.change_attribute',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def attributeAjaxUpdate(request,pk):
	if request.method=='GET':
		attribute=get_object_or_404(Attribute,id=pk)
		return JsonResponse({'status':'success','attribute':model_to_dict(attribute)})

	if request.method == 'POST':
		attribute= get_object_or_404(Attribute,id=pk)
		form=AttributeForm(request.POST,instance=attribute)
		if form.is_valid():
			form.save()
			messages.success(
		                    request, "Attribute has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

@permission_required('catalog.delete_attribute',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteAttributeBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
        	try:
	            Attribute.objects.filter(id=item_id[int(i)]).delete()
	            messages.success(request, "Selected attribute has been removed successfully.")
	        except ProtectedError:
	        	messages.error(request, "You cant delete some attribute until related product varient are deleted.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('catalog.delete_attribute',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def attributeDelete(request,pk):
	if request.method=='POST':
		try:
			get_object_or_404(Attribute,id=pk).delete()
			messages.success(request, "Attribute has been removed successfully.")
		except ProtectedError:
			messages.error(request, "You cant delete this attribute until related product varient are deleted.")
		return redirect('catalog:attribute-list')




@permission_required('catalog.view_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def addonList(request):
	if request.method=='GET':
		addons=ProductAddons.objects.order_by('-id')
		form=AddonForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			addons=ProductAddons.objects.filter(Q(name__icontains=keywords) | Q(price__icontains=keywords))
		return render(request,'admin_view/catalog/addons.html',{'addons':addons,'keywords':keywords,'form':form,})

@permission_required('catalog.delete_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def addonDelete(request,pk):
	if request.method=='POST':
		try:
			get_object_or_404(ProductAddons,id=pk).delete()
			messages.success(request, "Addons has been removed successfully.")
			return redirect('catalog:addons-list')
		except ProtectedError:
			messages.error(request, "Cannot delete this addon because it is related on order.")
			return redirect('catalog:addons-list')

@permission_required('catalog.add_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def addonCreate(request):
	if request.method=='GET':
		form =AddonForm()
		return  render(request,'admin_view/catalog/addon-create.html',{'form':form,})
	if request.method=='POST':
		form=AddonForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, "Addons has been added successfully.")
			return redirect('catalog:addons-list')
		return render(request,'admin_view/catalog/addon-create.html',{'form':form})

@permission_required('catalog.change_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def addonUpdate(request,pk):
	if request.method=='GET':
		addons=get_object_or_404(ProductAddons,id=pk)
		form=AddonForm(instance=addons)
		return render(request,'admin_view/catalog/addon-update.html',{'form':form,'addons':addons,})
	if request.method=='POST':
		addons=get_object_or_404(ProductAddons,id=pk)
		form=AddonForm(request.POST,request.FILES or None,instance=addons)
		if form.is_valid():
			form.save()
			messages.success(request, "Addon has been updated successfully.")
			return redirect('catalog:addons-list')
		return render(request,'admin_view/catalog/addon-update.html',{'form':form,'addons':addons})


@permission_required('catalog.delete_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteAddonBulk(request):
	"""Addon delete in bulk"""
	if request.method=='POST':
	    item_id=request.POST.getlist('foo',None)
	    try:
	        for i in range(0,len(item_id)):
	            coupon=ProductAddons.objects.filter(id=item_id[int(i)]).delete()
	        messages.success(request, "Selected addons has been removed successfully.")
	    except ProtectedError:
	    	messages.error(request, "Cannot delete some addon because they are related to order.")
	return redirect(request.META['HTTP_REFERER'])

@permission_required('catalog.change_productaddons',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def addonAvailableStatus(request):
	"""Updating category availability status via ajax"""
	if request.method=='GET':
		val=request.GET.get('val', None)
		item=request.GET.get('item-id', None)
		if val == 'True':
			is_available=True
		if val == 'False':
			is_available=False
		ProductAddons.objects.filter(id=item).update(is_active=is_available)
		return JsonResponse({'message':'Addon has been updated.'})



@permission_required('catalog.view_flavour',raise_exception=True)#
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourList(request):
	"""Liating flavour"""
	if request.method=='GET':
		flavour=Flavour.objects.order_by('-id')
		form=FlavourForm()
		keywords=request.GET.get('keywords',None)
		if keywords:
			flavour=Flavour.objects.filter(Q(name__icontains=keywords))
		return render(request,'admin_view/catalog/flavour.html',{'flavour':flavour,'keywords':keywords,'form':form})

@permission_required('catalog.add_flavour',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourAjaxCreate(request):

	"""Create flavour"""
	if request.method == 'POST':
		form = FlavourForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, "Flavour has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})



@permission_required('catalog.change_flavour',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourAjaxUpdate(request,pk):
	"""update flavour"""
	if request.method=='GET':
		flavour=get_object_or_404(Flavour,id=pk)
		return JsonResponse({'status':'success','addons':model_to_dict(flavour)})

	if request.method == 'POST':
		flavour= get_object_or_404(Flavour,id=pk)
		form=FlavourForm(request.POST,instance=flavour)
		if form.is_valid():
			form.save()
			messages.success(request, "Flavour has been Added Successfully")
			return JsonResponse({'status': 'success'})
		return JsonResponse({'errors': form.errors})

@permission_required('catalog.delete_flavour',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteFlavourBulk(request):
	"""Delete falvour in bulk"""
	if request.method=='POST':
	    item_id=request.POST.getlist('foo',None)
	    for i in range(0,len(item_id)):
	        tags=Flavour.objects.filter(id=item_id[int(i)]).delete()
	    messages.success(request, "Selected flavour has been removed successfully.")
	return redirect(request.META['HTTP_REFERER'])

@permission_required('catalog.delete_flavour',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def flavourDelete(request,pk):
	"""delete flavour """
	if request.method=='POST':
		flavour=get_object_or_404(Flavour,id=pk).delete()
		messages.success(request, "Flavour has been removed successfully.")
		return redirect('catalog:flavour-list')



# @user_passes_test(lambda u: u.is_superuser or u.is_staff)
# def IncreaseCakePrice(request):
# 	try:
# 		all_varient = ProductVarient.objects.filter(product__store__name='oho! cake').values('id')
# 		for i in all_varient:
# 			varient_id = i.get('id')
# 			var_obj = get_object_or_404(ProductVarient, id=varient_id)
# 			if var_obj.old_price:
# 				old_price_ = (var_obj.old_price)+(var_obj.old_price*0.2)
# 			else:
# 				old_price_ = 0
# 			if var_obj.price:
# 				price_ = (var_obj.price)+(var_obj.price*0.2)
# 			else:
# 				price_ = 0
# 			if var_obj.cost_price:
# 				cost_price_ = (var_obj.cost_price)+var_obj.cost_price*0.2
# 			else:
# 				cost_price_ = 0
# 			update = ProductVarient.objects.filter(id=varient_id).update(old_price=old_price_, price=price_, cost_price=cost_price_)
# 		return HttpResponse("successfully Update to the database")
# 	except Exception as e:
# 		return HttpResponse(str(e))

