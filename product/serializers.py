from rest_framework import serializers
from product.models import Product, Brand,ProductCategory, ProductSubCategory, SizeQuantityPrice,ProductDetailCategory,ProductImages
from dashboard.models import Reviews
class SizeQuantityPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeQuantityPrice
        fields = "__all__"






class category_serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class subcategory_serializer(serializers.ModelSerializer):
    category = category_serializer
    class Meta:
        model = ProductSubCategory
        fields = "__all__"


class detail_category_serializer(serializers.ModelSerializer):
    subcategory = subcategory_serializer
    class Meta:
        model = ProductDetailCategory
        fields = "__all__"


class ProductImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImages
        fields = ('img',)

class product_serializer(serializers.ModelSerializer):
    category = category_serializer()
    subcategory = subcategory_serializer()
    detail_category = detail_category_serializer()
    sqp = SizeQuantityPriceSerializer(many=True, read_only=True)
    images = ProductImagesSerializer(many=True, read_only=True, source='productimages_set')  # Assuming 'productimages_set' is the related name
    class Meta:
        model = Product
        fields = "__all__"
        
        
class size_quantity_price_serializer(serializers.ModelSerializer):
    class Meta:
        model = SizeQuantityPrice
        fields = "__all__"
    
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reviews
        fields = "__all__"
        


