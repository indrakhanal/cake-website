import imp
import json
from textwrap import indent
from django.contrib.auth.decorators import login_required
from requests import head, post
from accounts.forms import (UserUpdateForm,
    CustomLoginForm,
    CustomSignupForm,
    UserForm,
    ChangePasswordUserForm,
    UserCreateForm,
    ProfileForm)
from django.shortcuts import render, redirect, get_object_or_404
from allauth.account.views import (SignupView,ConfirmEmailView,LoginView,
    PasswordResetView,PasswordChangeView,PasswordSetView)
from django.contrib import messages
from django.contrib.auth import get_user_model
from catalog.models import *
from .models import *
from django.db.models import Q
from django.contrib import messages, auth
from django.views.generic import ListView,DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, JsonResponse
from django.views.generic import TemplateView, ListView, CreateView, DeleteView
import secrets
from client.views import CatalogView,BaseView
from store.models import Store
User = get_user_model()
from django.db.models import Q
from django.conf import settings as conf
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here

class SuperUserCheck(LoginRequiredMixin, UserPassesTestMixin):
    """Permission check for users and return true if user have permission.
    Used in class based views.
    """
    def __init__(self):
        super().__init__()
        self.request = None
        
    def handle_no_permission(self):
        messages.error(self.request,"Permission denied for this user")
        return redirect('accounts:admin-login')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

decorator_with_arguments = lambda decorator: lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)
@decorator_with_arguments
def custom_permission_required(function, perm,raise_exception):
    """
    Permission check for users and return true if user have permission.
    Used in class function based views.
    """
    def _function(request, *args, **kwargs):
        if request.user.has_perm(perm):
            return function(request, *args, **kwargs)
        else:
            messages.error(request,"Permission denied for this user")
            return redirect('accounts:admin-login')
    return _function

class LoginView(LoginView,CatalogView):
    """Login view for customers """
    template_name = 'account/clientstore_login.html'

    form_class = CustomLoginForm
    # signup_form  = CustomSignupForm
    def __init__(self, **kwargs):
        super(LoginView, self).__init__(*kwargs)        
 
    def get_context_data(self, **kwargs):
        ret = super(LoginView, self).get_context_data(**kwargs)
        ret['form'] = self.get_form()
        ret['page_title']="Login Page"
        return ret
login = LoginView.as_view()

class SignupView(SignupView,CatalogView):
    """Signup view for customer"""
    template_name = 'account/clientstore_signup.html'
 
    form_class = CustomSignupForm
    # signup_form  = CustomSignupForm
    def __init__(self, **kwargs):
        super(SignupView, self).__init__(*kwargs)        
 
    def get_context_data(self, **kwargs):
        ret = super(SignupView, self).get_context_data(**kwargs)
        ret['form'] = self.get_form()
        ret['page_title']="Sign Up Page"
        return ret
login = SignupView.as_view()

def login_cancelled(request):
    """Redirect to login page when user cancel social login, like facebook or gmail"""
    return redirect('accounts:login')

class CustomEmailConfirmView(BaseView):
    """Email confirmation view after signup"""
    template_name="account/verification_sent.html"
    def get(self, request):
        return super(CustomEmailConfirmView, self).get(request,page_title="Email Verification")

def superUserOnlyLogin(request):
    """Login for superuser, admin, staff to dashboard"""
    if request.method=='GET':
        if request.user.is_authenticated and request.user.is_superuser or request.user.is_staff:
            return redirect('dashboard:admin-dashboard')
        form=CustomLoginForm()
        return render(request,'admin_view/login.html',{'form':form})
    if request.method =='POST':
        form=CustomLoginForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            email=data['login']
            password=data['password']
            user = auth.authenticate(email=email, password=password)
            if (user is not None) and (user.is_superuser or user.is_staff):
                auth.login(request, user)
                messages.success(request, "Logged in Successfully!")
                return redirect('dashboard:admin-dashboard')
            else:
                messages.error(request, "Invalid Credentials")
                return render(request,'admin_view/login.html',{'form':form})
        else:
            form=CustomLoginForm(request.POST)
            return render(request,'admin_view/login.html',{'form':form})

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@custom_permission_required('auth.view_user',raise_exception=False)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def userList(request):
    """User list in dashboard, setting-->users"""
    if request.method=='GET':
        user=User.objects.all().select_related('profile')
        user_keywords=request.GET.get('user_keywords',None)
        user_type=request.GET.get('user_type',None)
        store=Store.objects.all()
        if user_keywords:
            user=user.filter(Q(username__icontains=user_keywords) | Q(first_name__icontains=user_keywords) |Q(last_name__icontains=user_keywords) | Q(email__icontains=user_keywords))
        if user_type == 'admin':
            user=user.filter(Q(is_staff=True) | Q(is_superuser=True))
        elif user_type == 'delivery-boy':
            user=user.filter(Q(profile__is_delivery_person=True))
        elif user_type == 'vendor':
            user=user.exclude(profile__store=None)
        elif user_type == 'dispatcher':
            user=user.filter(Q(profile__is_dispatcher=True))
        elif user_type == 'production':
            user = user.filter(Q(profile__is_production_manager=True))
        else:
            user=user
        form=UserForm()
        paginator = Paginator(user, 20)
        try:
           page = request.GET.get('page')
           user = paginator.get_page(page)
        except PageNotAnInteger:
           user = paginator.get_page(1)
        except EmptyPage:
           user = paginator.get_page(paginator.num_pages)
        return render(request,'admin_view/account/users.html',{'user_keywords':user_keywords,'user':user,'form':form,'store':store,'user_type':user_type,'page':page})

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# @receiver(post_save, sender=UserProfile)
# def send_costumer_to_odoo(sender, instance, created, **kwargs):
#     from decouple import config
#     import requests
#     from accounts.external_api import post_authenticate
#     base_url = "https://ohocakes.10orbits-erp.com"
#     url = "/api/res.partner"
#     obj = get_object_or_404(UserProfile, id=instance.id)
#     f_name = obj.user.first_name
#     l_name = obj.user.last_name
#     full_name = f_name+" "+l_name
#     email = obj.user.email
#     phone = obj.phone_number
#     try:
#         street = obj.store.location.name
#     except:
#         street = False
#     data = {
#         "name":full_name,
#         "email":email,
#         "phone":phone,
#         "street":street,
#     }
#     session_id, tokens, partner_id = post_authenticate()
#     if session_id != "error":
#         header = {
#             "access-token":tokens,
#             "Content-type": "application/jsonp",
#             "Cookie":session_id
#         }
#         res = requests.post(base_url+url, headers=header, data=json.dumps(data, indent=4))
       
#         if res.status_code == 200:
#             status = "success"
#         else:
#             status = "Failed"
#         print(status)
#         obj.status = status
#     else:
#         print("error")
        


@custom_permission_required('auth.delete_user',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteUser(request,pk):
    """Deleting users from dashboard."""
    user = get_object_or_404(User, pk=pk).delete()
    messages.success(request, "User has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])

class ForgetPasswordView(PasswordResetView,CatalogView):
    """Forget password to reset again"""
    template_name="account/password_reset.html"
    def get(self, request):
        return super(ForgetPasswordView, self).get(request,page_title="Password Reset")



class PasswordResetMessageView(CatalogView):
    """Shows success message after password reset """
    template_name="account/password_reset_done.html"
    def get(self, request):
        return super(PasswordResetMessageView, self).get(request,page_title="Password Reset done")


class CustomPasswordChangeView(PasswordChangeView,BaseView):
    """Changing password of users"""
    template_name="account/password_change.html"
    def get(self, request):
        return super(CustomPasswordChangeView, self).get(request,page_title="Change Password")

class CustomPasswordSetView(PasswordSetView,BaseView):
    """setting new password of not set earlier.
    Specially in case of social and gmail login,Password is not set"""
    template_name="account/password_set.html"
    def get(self, request):
        return super(CustomPasswordSetView, self).get(request,page_title="Set Password")



class CreateUsers(SuperUserCheck,PermissionRequiredMixin,TemplateView):
    """Creating users by admin"""
    template_name="admin_view/account/user_create.html"
    permission_required = 'auth.add_user'
    def get(self,request,*args,**kwargs):
        form=UserCreateForm()
        form2=ProfileForm()
        return super(CreateUsers,self).get(request,form=form,form2=form2)
    def post(self, request, *args, **kwargs):
        form=UserCreateForm(request.POST)
        form2=ProfileForm(request.POST)
        if form.is_valid() and form2.is_valid():
            data=form.cleaned_data
            User = get_user_model()
            username=data['first_name']
            if User.objects.filter(username=username).exists():
                username=username+secrets.token_hex(3)
            form=form.save(commit=False)
            form.username=username
            form.is_active=True
            form.save()
            groups=data['group']
            for i in groups:
                i.user_set.add(form)
            form.save()
            data2=form2.cleaned_data
            UserProfile.objects.create(user=form,is_delivery_person=data2['is_delivery_person'],
                store=data2['store'],
                factory = data2["factory"],
                phone_number=data2['phone_number'],is_dispatcher=data2['is_dispatcher'],is_vendor=data2['is_vendor'])
            messages.success(request, 'User has been added successfully.')
            return redirect('accounts:user-list')
        else:
            return super(CreateUsers,self).get(request,form=form,form2=form2)


@custom_permission_required('auth.change_user',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def updateUser(request,pk):
    """Updating user by admin"""
    if request.method=='GET':
        user=get_object_or_404(User,id=pk)
        groups=user.groups.all()
        form=UserForm(instance=user,initial={'group':groups})
        try:
            profile=UserProfile.objects.get(user=user)
        except:
            profile=None
        form2=ProfileForm(instance=profile)
        return render(request,'admin_view/account/user_update.html',{'form':form,'user':user,'form2':form2})
    if request.method=='POST':
        user=get_object_or_404(User,id=pk)
        try:
            profile=user.profile
        except:
            profile=None
        form=UserForm(request.POST,instance=user)
        form2=ProfileForm(request.POST,instance=profile)
        if form.is_valid() and form2.is_valid():
            data=form.cleaned_data
            form=form.save()
            groups=data['group']
            form.groups.clear()
            for i in groups:
                i.user_set.add(form)
            form.save()
            data2 = form2.cleaned_data
            form2=form2.save(commit=False)
            form2.user=form
            form2.factory = data2["factory"]
            form2.save()
            messages.success(request, 'User has been updated successfully.')
            return redirect('accounts:user-list')
        return render(request,'admin_view/account/user_update.html',{'form':form,'user':user,'form2':form2})




#bulk delete of users on dashboard
@custom_permission_required('auth.delete_user',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def deleteBulkUser(request):
    """Deleting user in bulk by admin"""
    if request.method=='POST':
        item_id=request.POST.getlist('foo',None)
        for i in range(0,len(item_id)):
            user=User.objects.filter(id=item_id[int(i)]).delete()
        messages.success(request, "Selected users has been removed successfully.")
    return redirect(request.META['HTTP_REFERER'])


@custom_permission_required('auth.change_user',raise_exception=True)
@user_passes_test(lambda u: u.is_superuser or u.is_staff )
def changePassword(request,pk):
    """change password of any users by admin"""
    if request.method=='POST':
        password=request.POST.get('password',None)
        password2=request.POST.get('password2',None)
        user=get_object_or_404(User,id=pk)
        if password==password2:
            user.set_password(password)
            user.is_active=True
            user.save()
            messages.success(request, "Password changed successfully.")
            return redirect('accounts:user-list')
        else:
            messages.error(request, "Password didnt match.")
            return redirect('accounts:user-list')



@login_required
def changePasswordUser(request,pk):
    if request.method=='POST':
        user=get_object_or_404(User,id=pk)
        form=ChangePasswordUserForm(request.POST)
        if form.is_valid():
            data=form.cleaned_data
            password1=data['password1']
            password2=data['password2']
            user.set_password(password1)
            user.save()
            messages.success(request, "Password changed successfully.")
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'errors':form.errors})


@login_required
def changeNameUser(request,pk):
    """client name change by themselves"""
    if request.method=='POST':
        user=get_object_or_404(User,id=pk)
        first_name=request.POST.get('first_name',None)
        last_name=request.POST.get('last_name',None)
        if first_name and last_name:
            user.first_name=first_name
            user.last_name=last_name
            user.save()
            messages.success(request, "Name changed successfully.")
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'errors':'Enter your both first and last name.'})


@login_required
def changePhoneUser(request,pk):
    """client phone number change by themselves"""
    if request.method=='POST':
        user=get_object_or_404(User,id=pk)
        phone=request.POST.get('phonenumber',None)
        if len(phone) < 10 or len(phone) > 11:
            return JsonResponse({'errors':'Invalid phone number.'})
        if phone:
            try:
                user.profile.phone_number=phone
                user.profile.save()
            except:
                UserProfile.objects.create(user=user,phone_number=phone)
            messages.success(request, "Phone number changed successfully.")
            return JsonResponse({'status':'success'})
        else:
            return JsonResponse({'errors':'Enter phone number.'})







