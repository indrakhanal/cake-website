from django.contrib import admin
from .models import *
admin.site.site_header = "Cake977"
admin.site.site_title = "Cake977 Admin Portal"
admin.site.index_title = "Welcome to Cake977"

class CategoryAdmin(admin.ModelAdmin):	
	list_display = ('name', 'parent','display_order','is_available','show_on_landing',)
	prepopulated_fields = {'slug': ('name',)}
	list_filter = ('parent', 'name',)
	search_fields = ['name',]
	list_display_links = ['name','parent','display_order']
admin.site.register(Category,CategoryAdmin)
class ProductAdmin(admin.ModelAdmin):	
	list_display = ('name','display_order','is_available','show_eggless','show_sugarless')
	prepopulated_fields = {'slug': ('name',)}
	list_filter = ('name',)
	search_fields = ['name']
	list_display_links = ['name','display_order']
admin.site.register(Product,ProductAdmin)

class ProductVarientAdmin(admin.ModelAdmin):	
	list_display = ('varient_name','product_code','display_order_varient','product','is_available_varient','status','quantity',)
	prepopulated_fields = {'slug': ('varient_name',)}
	list_filter = ('varient_name',)
	search_fields = ['varient_name']
	list_display_links = ['varient_name','display_order_varient']
admin.site.register(ProductVarient,ProductVarientAdmin)

class ProductReviewAdmin(admin.ModelAdmin):	
	list_display = ('review_text','review_star','product','customer','created_on','customer_purchased',)
	list_filter = ('review_text','review_star',)
	search_fields = ['varient_name','customer','product']
	list_display_links = ['review_text','review_star']
admin.site.register(ProductReview,ProductReviewAdmin)

admin.site.register([Flavour,Tags,Attribute,AttributeValue,ProductAddons,SessionImage])
