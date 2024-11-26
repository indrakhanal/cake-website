from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView

import debug_toolbar

from rest_framework_simplejwt import views as jwt_views

from rest_framework.documentation import include_docs_urls
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.views import get_swagger_view

API_TITLE = 'Cake-977 API' # new
API_DESCRIPTION = 'A Web API for creating and editing cake posts.'
schema_view = get_schema_view(title=API_TITLE)
# schema_view = get_swagger_view(title=API_TITLE)


urlpatterns = [
  path('superadmin/', admin.site.urls),

  path(
        "sitemap",
        TemplateView.as_view(template_name="client/cake-977/sitemap.xml", content_type="text/plain"),name='sitemap'
    ),
  
  path('api/', include('sales.api.urls')),
  path('api/',include('catalog.api.urls')),
  path('api/',include('store.api.urls')),
  path('api/',include('settings.api.urls')),
  path('api/',include('marketing.api.urls')),
  path('api/',include('landing.api.urls')),
  path('api/',include('NewsletterandContact.api.urls')),
  path('api-auth/', include('rest_framework.urls')),

  path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),


  path('', include('accounts.urls', namespace='accounts')),
  path('accounts/', include('allauth.urls')),
  path('', include('catalog.urls', namespace='catalog')),
  path('', include('client.urls', namespace='client')),
  path('', include('sales.urls', namespace='sales')),
  path('', include('marketing.urls', namespace='marketing')),
  path('', include('payment.urls', namespace='payment')),
  path('', include('utility.urls', namespace='utility')),
  path('', include('store.urls', namespace='store')),
  path('', include('landing.urls', namespace='landing')),
  path('', include('vendorAnddelivery.urls', namespace='vendorAndDelivery')),
  path('', include('NewsletterandContact.urls', namespace='newsletter-contact')),
  path('', include('schedulejob.urls', namespace = 'schedulejob')),
  path('settings/', include('settings.urls', namespace='settings')),
  path('dashboard/', include('dashboard.urls', namespace='dashboard')),
  path('ckeditor/', include('ckeditor_uploader.urls')),


  # path('__debug__/', include(debug_toolbar.urls)),

  path('docs/', include_docs_urls(title=API_TITLE,description=API_DESCRIPTION)),
  # path('schema/', schema_view),
  


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
