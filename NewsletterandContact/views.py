from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse,Http404
from django.http import JsonResponse
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.views import custom_permission_required as permission_required,SuperUserCheck

# from django.contrib.auth.decorators import permission_required
# Create your views here.





@permission_required('NewsletterandContact.view_subscriptionemail',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def emailList(request):
	if request.method=='GET':
		emails=SubscriptionEmail.objects.order_by('-id')
		
		keywords=request.GET.get('keywords',None)

		if keywords:
			emails=SubscriptionEmail.objects.filter(Q(email__icontains=keywords))
		return render(request,'admin_view/NewsletterandContact/subscription_emails.html',{'emails':emails,'keywords':keywords,})



@permission_required('NewsletterandContact.delete_subscriptionemail',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteEmailBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            emails=SubscriptionEmail.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected emails has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('NewsletterandContact.delete_subscriptionemail',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def emailDelete(request,pk):
	if request.method=='POST':
		email=get_object_or_404(SubscriptionEmail,id=pk).delete()
		messages.success(request, "Email has been removed successfully.")
		return redirect('newsletter-contact:sub-emails')






@permission_required('NewsletterandContact.view_contactmessage',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def contactList(request):
	if request.method=='GET':
		contacts=ContactMessage.objects.order_by('-id')
		keywords=request.GET.get('keywords',None)
		if keywords:
			contacts=ContactMessage.objects.filter(Q(first_name__icontains=keywords)|Q(last_name__icontains=keywords)|Q(contact_number__icontains=keywords))
		return render(request,'admin_view/NewsletterandContact/contact_message.html',{'contacts':contacts,'keywords':keywords})

@permission_required('NewsletterandContact.delete_contactmessage',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteContactBulk(request):
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            contact=ContactMessage.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected contact message has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

@permission_required('NewsletterandContact.delete_contactmessage',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def contactDelete(request,pk):
	if request.method=='POST':
		contact=get_object_or_404(ContactMessage,id=pk).delete()
		messages.success(request, "Contact message has been removed successfully.")
		return redirect('newsletter-contact:contact-message')
