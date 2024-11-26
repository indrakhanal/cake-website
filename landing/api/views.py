from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets,permissions,mixins
from landing.models import *
from .serializers import *
from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission,SAFE_METHODS
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import generics
import django_filters

class ListRetrieveSectionOneView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = SectionOne.objects.order_by('-id').all()
   serializer_class = SectionOneReadSerializer
   
class CreateUpdateDestroySectionOneView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = SectionOne.objects.order_by('-id').all()
   serializer_class = SectionOneWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class LandingCategoiresFilter(django_filters.FilterSet):
    class Meta:
        model = LandingCategories
        fields = ['is_active']

class ListRetrieveLandingCategoriesView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = LandingCategories.objects.order_by('-id').all()
   serializer_class = LandingCategoriesReadSerializer
   filter_class = LandingCategoiresFilter
   
class CreateUpdateDestroyLandingCategoriesView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = LandingCategories.objects.order_by('-id').all()
   serializer_class = LandingCategoriesWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class BestSellerSectionFilter(django_filters.FilterSet):
    class Meta:
        model = BestSellersSection
        fields = ['is_active']

class ListRetrieveBestSellersSectionView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = BestSellersSection.objects.order_by('-id').all()
   serializer_class = BestSellersSectionReadSerializer
   filter_class = BestSellerSectionFilter
   
class CreateUpdateDestroyBestSellersSectionView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = BestSellersSection.objects.order_by('-id').all()
   serializer_class = BestSellersSectionWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class LandingFullBannerFilter(django_filters.FilterSet):
    class Meta:
        model = LandingFullBanner
        fields = ['is_active']

class ListRetrieveLandingFullBannerView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = LandingFullBanner.objects.order_by('-id').all()
   serializer_class = LandingFullBannerReadSerializer
   filter_class = LandingFullBannerFilter
   
class CreateUpdateDestroyLandingFullBannerView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = LandingFullBanner.objects.order_by('-id').all()
   serializer_class = LandingFullBannerWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class PopularFlavourSectionFilter(django_filters.FilterSet):
    class Meta:
        model = PopularFlavourSection
        fields = ['is_active']

class ListRetrievePopularFlavourSectionView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = PopularFlavourSection.objects.order_by('-id').all()
   serializer_class = PopularFlavourSectionReadSerializer
   filter_class = PopularFlavourSectionFilter
   
class CreateUpdateDestroyPopularFlavourSectionView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = PopularFlavourSection.objects.order_by('-id').all()
   serializer_class = PopularFlavourSectionWriteSerializer
   permission_classes = (permissions.IsAdminUser,)

class ExploreStoreFilter(django_filters.FilterSet):
    class Meta:
        model = ExploreStore
        fields = ['is_active']

class ListRetrieveExploreStoreView(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           viewsets.GenericViewSet):
   queryset = ExploreStore.objects.order_by('-id').all()
   serializer_class = ExploreStoreReadSerializer
   filter_class = ExploreStoreFilter
   
class CreateUpdateDestroyExploreStoreView(mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
   queryset = ExploreStore.objects.order_by('-id').all()
   serializer_class = ExploreStoreWriteSerializer
   permission_classes = (permissions.IsAdminUser,)