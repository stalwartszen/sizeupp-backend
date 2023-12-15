from rest_framework import serializers
from .models import Cart
from authentication.models import *
from product.serializers import *
class CartSerializer(serializers.ModelSerializer):
    product = product_serializer
    class Meta:
        model = Cart
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'
    
class OrderserSerializer(serializers.ModelSerializer):
    class Meta:
        model= Order
        fields = '__all__'
