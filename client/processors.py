from django.shortcuts import get_object_or_404
from sales.models import Cart
from .utils import sessionCalculation
def cart_count(request):
	if request.user.is_authenticated:
		try:
			cart_count=get_object_or_404(Cart,user=request.user).cart_count()
		except:
			Cart.objects.create(user=request.user)
			cart_count=0
	else:
		cart_count=sessionCalculation(request).get('cart_count')

	return {'cart_count':cart_count}


   
    