from django.urls import path
from .views import *
app_name = 'accounts'

urlpatterns = [

# path('profile/',ProfileView.as_view(),name='profile'),
# path('profile/update/user/',UserUpdateView.as_view(),name='update-user'),
path('signup/',SignupView.as_view(),name='signup'), 
path('login/',LoginView.as_view(),name='login'),  
path('accounts/confirm-email/',CustomEmailConfirmView.as_view()),
# path('accounts/confirm-email/',VerifyEmailView.as_view(),name='account_email_verification_sent'),   
path('accounts/password/reset/',ForgetPasswordView.as_view()), 
path('accounts/password/reset/done/',PasswordResetMessageView.as_view()),

path('accounts/password/change/',CustomPasswordChangeView.as_view()),
path('accounts/password/set/',CustomPasswordSetView.as_view()),
# path('social/signup/',AlreadyRegisteredView.as_view()),
path('accounts/social/login/cancelled/', login_cancelled,name="login-canceled"),
path('admin/',superUserOnlyLogin,name='admin-login'),
 
path('user-list/',userList,name='user-list'),
path('user/delete/<int:pk>/',deleteUser,name='user-delete'),
path('user/bulk/delete/',deleteBulkUser,name='user-bulk-delete'),
path('create/users/', CreateUsers.as_view(),name="create-users"),
path('update/user/<int:pk>/',updateUser,name='update1-user'),

path('change/password/users/byadmin/<int:pk>/',changePassword,name='change-password'),
path('change/password/users/<int:pk>/',changePasswordUser,name='change-password-user'),


path('change/name/users/<int:pk>/',changeNameUser,name='change-name-user'),
path('change/phone/users/<int:pk>/',changePhoneUser,name='change-phone-user'),

]
