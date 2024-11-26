from allauth.account.forms import SignupForm ,LoginForm,ChangePasswordForm,ResetPasswordForm,ResetPasswordKeyForm,SetPasswordForm
from django import forms
# from captcha.fields import ReCaptchaField
from django.contrib.auth import get_user_model
from .models import UserProfile
from store.models import Store
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
User = get_user_model()

class CustomSignupForm(SignupForm):
    """Overriding allauth signup form"""
    def __init__(self, *args, **kwargs):
        super(CustomSignupForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'placeholder': 'Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={ 'placeholder': 'Password (again)'})
        self.fields['email'].widget = forms.TextInput(attrs={'type': 'email', 'placeholder': 'Email'})

    first_name = forms.CharField(max_length=30, label='First Name', widget=forms.TextInput
    (attrs={ 'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(max_length=30, label='Last Name', widget=forms.TextInput
    (attrs={'placeholder': 'Enter your last name'}))


    email = forms.CharField(max_length=30, label='Email', widget=forms.TextInput
    (attrs={ 'placeholder': 'Email'}))
    # captcha = ReCaptchaField(error_messages={'required': 'Captcha Error'})
    phone_number = forms.IntegerField(label='Phone Number', widget=forms.NumberInput
    (attrs={ 'placeholder': 'Enter your phone number'}))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        phone_number=self.cleaned_data['phone_number']
        profile=UserProfile()
        profile.user=user
        profile.phone_number=phone_number
        profile.save()
        return user


class CustomLoginForm(LoginForm):
    """Customer login form"""
    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'class':'form-control','type': 'email','placeholder': 'Email Address'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class':'form-control','placeholder': 'Password'})
        self.fields['remember'].widget = forms.CheckboxInput(attrs={'class':'custom-control-input','id':'customCheckremember'})


class CustomChangePasswordForm(ChangePasswordForm):
    """Customer login form"""
    def __init__(self, *args, **kwargs):
        super(CustomChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['oldpassword'].widget = forms.PasswordInput(attrs={'type': 'password', 'class': 'form-control','placeholder': 'Old Password'})
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New Password again'})

class CustomPasswordSetForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordSetForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New Password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New Password again'})

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model=User
        fields=('first_name','last_name','email',)

        widgets = {
        'first_name': forms.TextInput(attrs=({'class': 'form-control','placeholder':'Enter your first name.','id':'fname'})),
        'last_name': forms.TextInput(attrs=({'class': 'form-control','placeholder':'Enter your last name.','id':'lname'})),
        'email': forms.TextInput(attrs=({'class': 'form-control','placeholder':'Enter your email.','id':'email','disabled':''})),
        }


class CustomPasswordResetForm(ResetPasswordForm):
     def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget = forms.PasswordInput(attrs={'type':'email','class': 'form-control','placeholder': 'Email address'})
       
class CustomPasswordResetFromKeyForm(ResetPasswordKeyForm):
     def __init__(self, *args, **kwargs):
        super(CustomPasswordResetFromKeyForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New password'})
        self.fields['password2'].widget = forms.PasswordInput(attrs={'class': 'form-control','placeholder': 'New password again'})
       

class UserForm(forms.ModelForm):
    group = forms.ModelMultipleChoiceField(label='Groups',required=False, queryset=Group.objects.all(),
    widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple','data-toggle':'select2', 'multiple':'multiple','data-placeholder':'Choose ...'}))
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password','is_superuser','is_staff','is_active','group']
        exclude=['last_login','date_joined','password','username']

        widgets = {
        'first_name': forms.TextInput(attrs=({'placeholder': 'Please enter First  name.','class': 'form-control','required':'required'})),
        'last_name': forms.TextInput(attrs=({'placeholder': 'Please enter Last  name.','class': 'form-control','required':'required'})),
        'email': forms.EmailInput(attrs=({'placeholder': 'Please enter Email.','class': 'form-control','required':'required'})),
        }
        error_messages = {
        'username': {'required': 'Username Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'},
        'password': {'required': 'Please enter password.'},
        
        
    }

    def clean_email(self):
        email=self.cleaned_data['email']
        if email and User.objects.filter(email=email).count()>1:
            raise ValidationError('Email already exist.')
        return email



class ChangePasswordUserForm(forms.Form):
    password1=    forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Enter new password.','id':'password1','required':'required'}))
    password2=   forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':'Confirm new password.','id':'password2','required':'required'}))

    def clean(self):
        cleaned_data = super(ChangePasswordUserForm, self).clean()
        password = cleaned_data.get("password1")
        confirm_password = cleaned_data.get("password2")

        if password != confirm_password:
            raise forms.ValidationError(
                "Password and Confirm password does not match"
            )
        if len(password)<6:
            raise forms.ValidationError(
                "Atleast require 6 characters."
            )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields="__all__"
        exclude = ['status',]
      

class UserCreateForm(UserCreationForm):
    group = forms.ModelMultipleChoiceField(label='Groups',required=False, queryset=Group.objects.all(),
    widget=forms.SelectMultiple(attrs={'class': 'form-control select2-multiple','data-toggle':'select2', 'multiple':'multiple','data-placeholder':'Choose ...'}))
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Enter password again'
    class Meta:
        fields = ['first_name','last_name','username','email','password1','password2','is_superuser','is_staff','is_active']
        exclude=['username',]
        model = get_user_model()
        widgets = {
        'first_name': forms.TextInput(attrs=({'placeholder': 'Please enter First  name.','class': 'form-control','required':'required'})),
        'last_name': forms.TextInput(attrs=({'placeholder': 'Please enter Last  name.','class': 'form-control','required':'required'})),
        'email': forms.EmailInput(attrs=({'placeholder': 'Please enter Email.','class': 'form-control','required':'required'})),
        }

        error_messages = {
        'username': {'required': 'Username Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'},
        'password1': {'required': 'Please enter password.'},
        'password2': {'required': 'Please enter confirm password.'},
        'email': {'required': 'Please enter email.'},
        }

    def clean(self):
        cleaned_data = super(UserCreateForm, self).clean()
        email = cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email already exists."
            )
