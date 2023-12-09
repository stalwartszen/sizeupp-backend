from rest_framework import serializers
from product.models import Product, Brand,ProductCategory, ProductDetailCategory, ProductSubCategory, SizeQuantityPrice
import json
from django.core.serializers import serialize

class SizeQuantityPriceSerializer(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SizeQuantityPrice):
            serialized_obj = serialize('json', [obj])
            deserialized_obj = json.loads(serialized_obj)[0]['fields']
            deserialized_obj['id'] = str(obj.id)
            return deserialized_obj
        return super().default(obj)


class brand_serializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = "__all__"




class category_serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class subcategory_serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = "__all__"


class detail_category_serializer(serializers.ModelSerializer):
    class Meta:
        model = ProductDetailCategory
        fields = "__all__"


class size_quantity_price_serializer(serializers.ModelSerializer):
    class Meta:
        model = SizeQuantityPrice
        fields = "__all__"
        


class product_serializer(serializers.ModelSerializer):
    category = category_serializer()
    brand = brand_serializer()
    subcategory = subcategory_serializer()
    detail_category = detail_category_serializer()
    size_quantity_price = size_quantity_price_serializer(many=True,read_only=True)
    class Meta:
        model = Product
        fields = "__all__"