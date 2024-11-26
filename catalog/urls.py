from django.urls import path
# from .views import *
from django.views.generic import TemplateView
from .views import *
app_name = 'catalog'

urlpatterns = [
path('category/',categoryList, name='category'),
path('ajax/category/create/',ajaxCategoryCreate,name='ajax-category-create'),
path('category/create/',CategoryCreate,name='category-create'),
path('category/delete/<int:pk>/', deleteCategory, name='category-delete'),
path('category/bulk/delete/',deleteCategoryBulk,name='category-bulk-delete'),

path('category/update/<int:pk>/', updateCategory, name='category-update'),

path('product/excel/upload/',excelUpload,name='excel-upload'),



path('<slug:slug>/product/',productList, name='product'),
path('<slug:slug>/product/create/',ProductCreate,name='product-create'),
path('ajax/product/create/<slug:slug>/',ajaxProductCreate,name='ajax-product-create'),
path('<int:pk>/<slug:slug>/product/delete/', deleteProduct, name='product-delete'),
path('product/bulk/delete/',deleteProductBulk,name='product-bulk-delete'),
path('<int:pk>/<slug:slug>/product/update/', updateProduct, name='product-update'),
path('excel/download/', download, name='excel-download'),
# path('varient-delete/<int:pk>/',deleteProductVarient,name='delete-varient'),


path('ajax/category/status/update/',catAvailableStatus,name='cat-available-status'),
path('ajax/product/status/update/',proAvailableStatus,name='pro-available-status'),


# path('ajax/varient/create/',ajaxVarientCreate,name='varient-create'),


path('addons/',addonList,name="addons-list"),
path('addons/delete/<int:pk>/',addonDelete,name="addons-delete"),
path('addons-create/',addonCreate,name="addons-create"),
# path('ajax/addons/create/',addonAjaxCreate,name="ajax-addons-create"),
path('addons-update/<int:pk>/',addonUpdate,name="addons-update"),
# path('ajax/addons/update/<int:pk>/',addonAjaxUpdate,name="ajax-addons-update"),
path('addons/bulk/delete/',deleteAddonBulk,name='addons-bulk-delete'),
path('addon-status-update/',addonAvailableStatus, name = 'addon-status-update'),

path('tags/',tagsList,name="tags-list"),
path('tags/delete/<int:pk>/',tagsDelete,name="tags-delete"),
path('ajax/tags/create/',tagsAjaxCreate,name="ajax-tags-create"),
path('ajax/tags/update/<int:pk>/',tagAjaxUpdate,name="ajax-tags-update"),
path('tags/bulk/delete/',deleteTagsBulk,name='tags-bulk-delete'),

path('attribute/',attributeList,name="attribute-list"),
path('attribute/delete/<int:pk>/',attributeDelete,name="attribute-delete"),
path('ajax/attribute/create/',attributeAjaxCreate,name="ajax-attribute-create"),
path('ajax/attribute/update/<int:pk>/',attributeAjaxUpdate,name="ajax-attribute-update"),
path('attribute/bulk/delete/',deleteAttributeBulk,name='attribute-bulk-delete'),


path('flavour/',flavourList,name="flavour-list"),
path('flavour/delete/<int:pk>/',flavourDelete,name="flavour-delete"),
path('ajax/flavour/create/',flavourAjaxCreate,name="ajax-flavour-create"),
path('ajax/flavour/update/<int:pk>/',flavourAjaxUpdate,name="ajax-flavour-update"),
path('flavour/bulk/delete/',deleteFlavourBulk,name='flavour-bulk-delete'),
# path('increase/', IncreaseCakePrice, name='increase')
]
