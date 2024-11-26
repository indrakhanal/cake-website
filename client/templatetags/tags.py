# from django import template 
# register = template.Library() 
# from catalog.models import Brand

# @register.simple_tag
# def brandCountCategoryWise(slug):
# 	print(slug,'------------------')
# 	return Brand.brandProductCountInCategory(slug)

# @register.filter(slug='cut')
# def brandCountCategoryWise(value, arg):
#     return Brand.brandProductCountInCategory(slug)