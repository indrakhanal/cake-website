from rest_framework import serializers
from store.models import *
from django.contrib.auth.models import User
from catalog.models import Product
from landing.models import *


class SectionOneSerializer(serializers.ModelSerializer):
   class Meta:
      model = SectionOne
      fields = '__all__'
class LandingCategoriesSerializer(serializers.ModelSerializer):
   class Meta:
      model = LandingCategories
      fields = '__all__'

class BestSellersSectionSerializer(serializers.ModelSerializer):
   class Meta:
      model = BestSellersSection
      fields = '__all__'

class LandingFullBannerSerializer(serializers.ModelSerializer):
   class Meta:
      model = LandingFullBanner
      fields = '__all__'

class PopularFlavourSectionSerializer(serializers.ModelSerializer):
   class Meta:
      model = PopularFlavourSection
      fields = '__all__'

class ExploreStoreSerializer(serializers.ModelSerializer):
   class Meta:
      model = ExploreStore
      fields = '__all__'



class LocationReadSerializer(serializers.ModelSerializer):
   section_one = SectionOneSerializer(many=True,read_only=True)
   landing_categories = LandingCategoriesSerializer(many=True,read_only=True)
   best_seller_section = BestSellersSectionSerializer(many=True,read_only=True)
   full_banner = LandingFullBannerSerializer(many=True,read_only=True)
   popular_flavour = PopularFlavourSectionSerializer(many=True,read_only=True)
   explore_stores = ExploreStoreSerializer(many=True,read_only=True)
   class Meta:
      model = Location
      fields = '__all__'
class LocationWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Location
      fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = '__all__'

class StoreReadSerializer(serializers.ModelSerializer):
   location = LocationWriteSerializer(many=True,read_only=True)
   product = ProductSerializer(many=True,read_only=True,source='store_product')
   class Meta:
      model = Store
      fields = '__all__'

class StoreWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Store
      fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
   class Meta:
      model = User
      fields = '__all__'

class StoreReviewReadSerializer(serializers.ModelSerializer):
   store = StoreWriteSerializer(many=False,read_only=True)
   # customer = UserSerializer(many=False,read_only=True)
   class Meta:
      model = StoreReview
      fields = '__all__'

class StoreReviewWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = StoreReview
      fields = ('id','review_text','review_star',)


class StoreSerializers(serializers.ModelSerializer):
   class Meta:
      model = Store
      fields = ('name','contact_number','store_location1',)

