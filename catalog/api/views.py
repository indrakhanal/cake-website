from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,permissions,mixins
from catalog.models import *
from sales.models import *
from .serializers import *
from store.models import Location as StoreLocation
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed
from django.db.models import Q, Avg, Max, Min



class CategoryFilter(django_filters.FilterSet):
    class Meta:
        model = Category
        fields = ['name','is_available','show_on_landing']

class RetrieveCategoryProductView(mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Category.objects.order_by('-id').all()
   serializer_class = CategoryReadSerializer

   # def get(self, request,location,category_slug):
   #      user=self.request.user
   #      print('user',user)
   #      category_slug=self.kwargs.get('category_slug')
   #      get_location=get_object_or_404(StoreLocation,name=location)
   #      print('location',get_location)
   #      products = Product.objects.filter(category__slug=category_slug,store__is_active=True, is_available=True,store__location=get_location.id)
   #      print('products',products)
   #      if products:
   #        serializer = ProductReadSerializer(products,many=True)
   #        return Response(serializer.data)
   #      else:
   #        return Response({'message':'fail:product is not available'})

   def retrieve(self,request,keyword,cate_slug,location):
      print('keyword',keyword)
      print('cate_slug',cate_slug)
      print('location',location)
      category_slug=self.kwargs.get('cate_slug')
      get_location=get_object_or_404(StoreLocation,name=location)

      category = get_object_or_404(Category, slug=category_slug)
      cat_descendants = category.get_descendants(include_self=True).filter(is_available=True)
      cat_all_children = category.get_descendants(include_self=False).filter(is_available=True)

      if keyword == "price-hl":
         products = Product.objects.filter(store__is_active=True, is_available=True,store__location=get_location,
                                              category__in=cat_descendants).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('-max_price','-max_price_2')
      elif keyword == "price-lh":
         products = Product.objects.filter(store__is_active=True, is_available=True,store__location=get_location,
                                              category__in=cat_descendants).annotate(max_price = Max('product__old_price'),max_price_2 = Max('product__price')).distinct().order_by('max_price','max_price_2')
      elif keyword == 'rating':   
         products = Product.objects.filter(store__is_active=True, is_available=True,store__location=get_location,
         category__in=cat_descendants).annotate(product_review__review_star=Avg('product_review__review_star')).prefetch_related(
                'tags').distinct().order_by('-product_review__review_star')
      else:
         products = Product.objects.filter(store__is_active=True, is_available=True,store__location=get_location,
         category__in=cat_descendants).prefetch_related('tags').distinct()

      if products:
         serializer = ProductReadSerializer(products,many=True)
         return Response(serializer.data)
      else:
         return Response({'message':'fail:product is not available'})



class ListRetrieveCategoryView(mixins.ListModelMixin,
                           # mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = Category.objects.order_by('-id').all()
    serializer_class = CategoryReadSerializer
    filter_class = CategoryFilter


class CreateUpdateDestroyCategoryView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Category.objects.order_by('-id').all()
   serializer_class = CategoryWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

# class BrandFilter(django_filters.FilterSet):
#     class Meta:
#         model = Brand
#         fields = ['name']

# class ListRetrieveBrandView(mixins.ListModelMixin,
#                            mixins.RetrieveModelMixin,
#                            viewsets.GenericViewSet):
#    queryset = Brand.objects.all()
#    serializer_class = BrandSerializer
#    filter_class = BrandFilter

# class CreateUpdateDestroyBrandView(mixins.CreateModelMixin,
#                            mixins.UpdateModelMixin,
#                            mixins.DestroyModelMixin,
#                            viewsets.GenericViewSet):

#    queryset = Brand.objects.all()
#    serializer_class = BrandSerializer
#    permission_classes = (permissions.IsAdminUser,)

class TagsFilter(django_filters.FilterSet):
    class Meta:
        model = Tags
        fields = ['name']

class ListRetrieveTagsView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Tags.objects.order_by('-id').all()
   serializer_class = TagsSerializer
   filter_class = TagsFilter

class CreateUpdateDestroyTagsView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Tags.objects.order_by('-id').all()
   serializer_class = TagsSerializer
   permission_classes = (permissions.IsAdminUser,)

class FlavourFilter(django_filters.FilterSet):
    class Meta:
        model = Flavour
        fields = ['name']


class ListRetrieveFlavourView(mixins.ListModelMixin,
                           # mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Flavour.objects.order_by('-id').all()
   serializer_class = FlavourReadSerializer
   filter_class = FlavourFilter

class RetrieveProductsThroughFlavour(generics.RetrieveAPIView):
  queryset = Flavour.objects.order_by('-id').all()
  serializers_class = FlavourReadSerializer
  def retrieve(self, request,pk,location):
        get_location=get_object_or_404(StoreLocation,name=location)
        products = Product.objects.filter(
                Q(flavour__id=pk) & Q(is_available=True) & Q(store__is_active=True),store__location=get_location).distinct().order_by(
                '-product__old_price')
        print('products',products)
        if products:
            serializer = ProductReadSerializer(products,many=True)
            return Response(serializer.data)
        else:
           return Response({'message':'fail:product is not available'},status=401)

class CreateUpdateDestroyFlavourView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Flavour.objects.order_by('-id').all()
   serializer_class = FlavourWriteSerializer
   permission_classes = (permissions.IsAdminUser,)





class ProductAddonsFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    class Meta:
        model = ProductAddons
        fields = ['name','min_price', 'max_price']


class ListRetrieveProductAddonsView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = ProductAddons.objects.order_by('-id').all()
   serializer_class = ProductAddonsSerializer
   filter_class = ProductAddonsFilter

class CreateUpdateDestroyProductAddonsView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = ProductAddons.objects.order_by('-id').all()
   serializer_class = ProductAddonsSerializer
   permission_classes = (permissions.IsAdminUser,)

class StandardResultsSetPagination(PageNumberPagination):
   page_size = 10
   page_size_query_param = 'page_size'
   max_page_size = 100
class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        fields = ['name','store__name','addons__name','flavour__name','tags__name','shipping_method__name','is_available','is_best_seller','show_eggless','show_sugarless','is_recomended']
   
class ListRetrieveProductView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Product.objects.order_by('-id').all()
   serializer_class = ProductReadSerializer
   filter_class = ProductFilter
   pagination_class = StandardResultsSetPagination
   lookup_field = 'slug'

class CreateUpdateDestroyProductView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Product.objects.order_by('-id').all()
   serializer_class = ProductWriteSerializer
   permission_classes = (permissions.IsAdminUser,)
   
class AttributeFilter(django_filters.FilterSet):
    class Meta:
        model = Attribute
        fields = ['name']

class ListRetrieveAttributeView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Attribute.objects.order_by('-id').all()
   serializer_class = AttributeSerializer
   filter_class = AttributeFilter

class CreateUpdateDestroyAttributeView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Attribute.objects.order_by('-id').all()
   serializer_class = AttributeSerializer
   permission_classes = (permissions.IsAdminUser,)

class AttributeValueFilter(django_filters.FilterSet):
    class Meta:
        model = AttributeValue
        fields = ['attribute__id']
class ListRetrieveAttributeValueView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = AttributeValue.objects.order_by('-id').all()
   serializer_class = AttributeValueReadSerializer
   filter_class= AttributeValueFilter

class CreateUpdateDestroyAttributeValueView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = AttributeValue.objects.order_by('-id').all()
   serializer_class = AttributeValueWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class StandardResultsSetPagination(PageNumberPagination):
   page_size = 20
   page_size_query_param = 'page_size'
   max_page_size = 100

class ProductVarientFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="price", lookup_expr='lte')
    class Meta:
        model = ProductVarient
        fields = ['varient_name','min_price', 'max_price','is_available_varient','base_varient']


class ListRetrieveProductVarientView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = ProductVarient.objects.order_by('-id').all()
   serializer_class = ProductVarientReadSerializer
   filter_class = ProductVarientFilter
   pagination_class = StandardResultsSetPagination
   lookup_field = "slug"

class CreateUpdateDestroyProductVarientView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = ProductVarient.objects.order_by('-id').all()
   serializer_class = ProductVarientWriteSerializer
   permission_classes = (permissions.IsAdminUser,)


class ProductReviewFilter(django_filters.FilterSet):
    class Meta:
        model = ProductReview
        fields = ['customer_purchased']

class ListRetrieveProductReviewView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = ProductReview.objects.order_by('-id').all()
   serializer_class = ProductReviewReadSerializer
   filter_class = ProductReviewFilter

class CreateUpdateProductReviewView(generics.CreateAPIView):

   queryset = ProductReview.objects.order_by('-id').all()
   serializer_class = ProductReviewWriteSerializer
   # permission_classes = (permissions.IsAuthenticated,)
   # print('id',pk)

   def create(self, request,pk):
        print('id',pk)
        print("---------------------")
        user=self.request.user
        product=get_object_or_404(Product,id=pk)
        point=request.data.get('review_star')
        comment=request.POST.get('review_text')
        print('point',point)
        print('comment',comment)
        customer_purchase_item = OrderItem.customer_purchased_item(user,product)
        print('customer_purchased',customer_purchase_item)
      #   if customer_purchase_item:
      #     ProductReview.create_product_review(comment, point, product, user, customer_purchased=False)
      #     return Response({'message':'success:review create successfully'}, status=status.HTTP_201_CREATED)
      #   else:
      #     return Response({'message':'fail:permission of review creation denied'}, status=status.HTTP_201_CREATED)

        if customer_purchase_item and ProductReview.objects.filter(customer=user,product=product):
          review=ProductReview.objects.get(customer=user,product=product)
          ProductReview.update_product_review(user, product, review, point, comment,customer_purchased=False)
          return Response({'message':'success:updated successfully'}, status=status.HTTP_201_CREATED)
        elif customer_purchase_item:
          ProductReview.create_product_review(comment, point, product, user, customer_purchased=False)
          return Response({'message':'success:review create successfully'}, status=status.HTTP_201_CREATED)
        else:
          return Response({'message':'fail:permission or review update denied'},status=401)

class DestroyProductReviewView(generics.DestroyAPIView):
   queryset = ProductReview.objects.order_by('-id').all()
   serializer_class = ProductReviewReadSerializer
   permission_classes = (permissions.IsAdminUser,)

   def destroy(self, request,pk):
        user=self.request.user
        product_review=get_object_or_404(ProductReview,customer=user,id=pk)
        if product_review:
           product_review.delete()
           return Response({'message':'success:review deleted successfully'}, status=status.HTTP_201_CREATED)
        else:
           return Response({'message':'fail:permission delete denied'})


class ProductSearchView(generics.RetrieveAPIView):
   queryset = Product.objects.order_by('-id').all()
   serializer_class = ProductReadSerializer
   # filter_class = ProductFilter
   pagination_class = StandardResultsSetPagination
   def get(self, request,keyword):
        user=self.request.user
        print('user',user)
        keywords=self.kwargs.get('keyword')
      #   print('category',category_slug)
        products = Product.objects.filter(Q(name__icontains=keywords) |
                                              Q(category__name__icontains=keywords) |
                                              Q(store__name__icontains=keywords) |
                                              Q(store__location__name__icontains=keywords) |
                                              Q(brand__name__icontains=keywords) & Q(
                Q(store__is_active=True) & Q(is_available=True))).distinct().order_by('-product__old_price')
        print('products',products)
        serializer = ProductReadSerializer(products,many=True)
        return Response(serializer.data)

      #   category=get_object_or_404(Category,slug=category_slug)
      #   if category:
      #     product=get_object_or_404(Product,slug=product_slug)
      #     print('category',category)
      #     print('product',product)
      #     serializer = ProductReadSerializer(product)
      #     return Response(serializer.data)
      #   else:
      #     pass    

