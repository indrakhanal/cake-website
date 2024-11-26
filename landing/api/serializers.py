from rest_framework import serializers
from landing.models import *
from catalog.api.serializers import CategoryWriteSerializer,ProductWriteSerializer,FlavourWriteSerializer
from store.api.serializers import StoreWriteSerializer,LocationWriteSerializer

class SectionOneReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   class Meta:
      model = SectionOne
      fields = '__all__'

class SectionOneWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = SectionOne
      fields = '__all__'

class LandingCategoriesReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   category = CategoryWriteSerializer(many=False,read_only=True)
   class Meta:
      model = LandingCategories
      fields = '__all__'

class LandingCategoriesWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = LandingCategories
      fields = '__all__'


class BestSellersSectionReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   product = ProductWriteSerializer(many=False,read_only=True)
   class Meta:
      model = BestSellersSection
      fields = '__all__'

class BestSellersSectionWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = BestSellersSection
      fields = '__all__'

class LandingFullBannerReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   class Meta:
      model = LandingFullBanner
      fields = '__all__'

class LandingFullBannerWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = LandingFullBanner
      fields = '__all__'

class PopularFlavourSectionReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   flavour = FlavourWriteSerializer(many=False,read_only=True)
   class Meta:
      model = PopularFlavourSection
      fields = '__all__'

class PopularFlavourSectionWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = PopularFlavourSection
      fields = '__all__'

class ExploreStoreReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=False,read_only=True)
   store = StoreWriteSerializer(many=False,read_only=True)
   class Meta:
      model = ExploreStore
      fields = '__all__'

class ExploreStoreWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = ExploreStore
      fields = '__all__'

