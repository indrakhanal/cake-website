from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,permissions,mixins
from store.models import *
from store.models import Location as StoreLocation
from .serializers import *
from catalog.api.serializers import ProductReadSerializer
from catalog.models import Product
from django.db.models import Q, Avg, Max, Min
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import django_filters
from django_filters import rest_framework as filters
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.exceptions import MethodNotAllowed

class LocationFilter(django_filters.FilterSet):
    class Meta:
        model = Location
        fields = ['name',]
class ListRetrieveLocationView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
    queryset = Location.objects.order_by('-id').all()
    serializer_class = LocationReadSerializer
    filter_class = LocationFilter
    lookup_field ="slug"

# class RetrieveLocationView(mixins.RetrieveModelMixin,
#                            viewsets.GenericViewSet):
#     queryset = Location.objects.order_by('-id').all()
#     serializer_class = LocationReadSerializer
#     # filter_class = LocationFilter
#     lookup_field = "slug"

   #  def retrieve(self, request,slug):
   #      # location_slug = request.GET.get('store_locations', None)
   #      print('slug',slug)
   #      location = get_object_or_404(Location, slug=slug)
   #      # print('location',location)
   #      product= Product.objects.filter(Q(store__location__slug=slug) & Q(store__is_active=True) & Q(
   #              is_available=True)).distinct().order_by('-id')
   #      print('products',product)
   #      serializer = ProductReadSerializer(product,many=True)
   #      return Response(serializer.data)


class CreateUpdateDestroyLocationView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Location.objects.order_by('-id').all()
   serializer_class = LocationWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class StoreFilter(django_filters.FilterSet):
    class Meta:
        model = Store
        fields = ['name','flat_eggless']

class StandardResultsSetPagination(PageNumberPagination):
   page_size = 10
   page_size_query_param = 'page_size'
   max_page_size = 100

class ListStoreView(mixins.ListModelMixin,
                           # mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = Store.objects.order_by('-id').all()
   serializer_class = StoreReadSerializer
   filter_class =StoreFilter
   pagination_class = StandardResultsSetPagination
   def list(self,request,location,filter_value):
      get_location=get_object_or_404(StoreLocation,name=location)
      print('get_location',get_location)
      if filter_value=='rating':
            stores = Store.objects.filter(is_active=True,location=get_location).annotate(product_review__review_star=Avg('store_review__review_star')).distinct().order_by('-store_review__review_star')
      else:
         stores = Store.objects.filter(is_active=True,location=get_location)
         print('stores',stores)
      if stores:
         serializer = StoreReadSerializer(stores,many=True)
         return Response(serializer.data)
      else:
         return Response({'message':'fail:store is not available'})

class RetrieveStoreView(generics.RetrieveAPIView):
   queryset = Store.objects.order_by('-id').all()
   serializer_class = StoreReadSerializer
   def retrieve(self, request,location,store_slug):
        get_location = get_object_or_404(Location, name=location)
        products = Product.objects.filter(store__slug=store_slug,store__is_active=True, 
        is_available=True,store__location=get_location)
        if products:
           serializer = ProductReadSerializer(products,many=True)
           return Response(serializer.data)
        else:
           return Response({'message':'fail:store doesnot have products'},status=status.HTTP_201_CREATED)


class CreateUpdateDestroyStoreView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = Store.objects.order_by('-id').all()
   serializer_class = StoreWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class StoreReviewFilter(django_filters.FilterSet):
    class Meta:
        model = StoreReview
        fields = ['customer_purchased']
class ListRetrieveStoreReviewView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = StoreReview.objects.order_by('-id').all()
   serializer_class = StoreReviewReadSerializer
   filter_class = StoreReviewFilter

class CreateUpdateDestroyStoreReviewView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):

   queryset = StoreReview.objects.order_by('-id').all()
   serializer_class = StoreReviewWriteSerializer
   permission_classes = (permissions.IsAuthenticated,)

class CreateUpdateStoreReviewView(generics.CreateAPIView):

   queryset = StoreReview.objects.order_by('-id').all()
   serializer_class = StoreReviewWriteSerializer
   # permission_classes = (permissions.IsAuthenticated,)
   # print('id',pk)

   def create(self, request,pk):
        print('id',pk)
        print("--------------------")
        user=self.request.user
        store=get_object_or_404(Store,id=pk)
        point=request.data.get('review_star')
        comment=request.POST.get('review_text')
        print('point',point)
        print('comment',comment)
        
        if StoreReview.objects.filter(customer=user,store=store):
            print('hello world')
            review=StoreReview.objects.get(customer=user,store=store)
            update = StoreReview.update_store_review(user, store, review, point, comment,customer_purchased=False)
            if update:
               return Response({'message':'success:store review updated successfully'}, status=status.HTTP_201_CREATED)
            else:
               return Response({'message':'fail:store review update fail'}, status=status.HTTP_201_CREATED)
        else:
            create = StoreReview.create_store_review(comment, point, store, user, customer_purchased=False)
            if create:
               return Response({'message':'success: store review create successfully'}, status=status.HTTP_201_CREATED)
            else:
               return Response({'message':'fail: store review create fail'}, status=status.HTTP_201_CREATED)
        return Response({'message':'fail:permission or review update denied'})  


class DestroyStoreReviewView(mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = StoreReview.objects.order_by('-id').all()
   serializer_class = StoreReviewWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

   
