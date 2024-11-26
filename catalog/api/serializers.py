from rest_framework import serializers
from catalog.models import *
from store.api.serializers import StoreWriteSerializer
from settings.api.serializers import ShippingMethodWriteSerializer


# class BrandSerializer(serializers.ModelSerializer):
#    class Meta:
#       model = Brand
#       fields = '__all__'

class TagsSerializer(serializers.ModelSerializer):
   class Meta:
      model = Tags
      fields = '__all__'


class FlavourWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Flavour
      fields = '__all__'

class ProductAddonsSerializer(serializers.ModelSerializer):
   class Meta:
      model = ProductAddons
      fields = '__all__'

class ProductWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = '__all__'

class FlavourReadSerializer(serializers.ModelSerializer):
   product = ProductWriteSerializer(many=True,read_only=True,source='flavour')
   class Meta:
      model = Flavour
      fields = '__all__'


class CategoryReadSerializer(serializers.ModelSerializer):
   # url = serializers.HyperlinkedIdentityField(view_name='catalog:get-categories',read_only=True,lookup_field='pk',many=False)
   # product = ProductWriteSerializer(many=True,read_only=True,source='category')
   class Meta:
      model = Category
      fields = '__all__'
      # fields = ('url','id','slug','name','description','parent','image','index_image_thumbnail','is_available','show_on_landing','display_order','product')
      # lookup_field = 'slug'
      # extra_kwargs = {
      #       'url': {'lookup_field': 'slug'}
      #   }

class CategoryWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = Category
      fields = '__all__'


class ProductReadSerializer(serializers.ModelSerializer):
   store = StoreWriteSerializer(many=False,read_only=True)
   category = CategoryWriteSerializer(many=True,read_only=True)
   addons = ProductAddonsSerializer(many=True,read_only=True)
   # brand = BrandSerializer(many=False,read_only=True)
   tags = TagsSerializer(many=False,read_only=True)
   shipping_method = ShippingMethodWriteSerializer(many=True,read_only=True)
   flavour = FlavourWriteSerializer(many=True,read_only=True)
   
   class Meta:
      model = Product
      fields = '__all__'


class AttributeSerializer(serializers.ModelSerializer):
   class Meta:
      model = Attribute
      fields = '__all__'

class AttributeValueReadSerializer(serializers.ModelSerializer):
   attribute = AttributeSerializer(many=False,read_only=True)
   class Meta:
      model = AttributeValue
      fields = '__all__'

class AttributeValueWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = AttributeValue
      fields = '__all__'

class ProductVarientReadSerializer(serializers.ModelSerializer):
   product=ProductWriteSerializer(many=False,read_only=True)
   attribut_value = AttributeValueWriteSerializer(many=True,read_only=True)
   class Meta:
      model = ProductVarient
      fields = '__all__'

class ProductVarientWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = ProductVarient
      fields = '__all__'

class ProductReviewReadSerializer(serializers.ModelSerializer):
   product=ProductWriteSerializer(many=False,read_only=True)
   class Meta:
      model = ProductReview
      fields = '__all__'

class ProductReviewWriteSerializer(serializers.ModelSerializer):
   class Meta:
      model = ProductReview
      # fields='__all__'
      fields = ('id','review_text','review_star',)








