from rest_framework import serializers
from .models import Cart
from authentication.models import *
from product.serializers import *
class UserSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    product = product_serializer()
    class Meta:
        model = Cart
        fields = '__all__'
        
class WishListSerializer(serializers.ModelSerializer):
    product = product_serializer()
    class Meta:
        model = WishList
        fields = '__all__'

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'



class OrderItemserSerializer(serializers.ModelSerializer):
    product = product_serializer()
    class Meta:
        model= OrderItem
        fields = '__all__'
        
            
class OrderserSerializer(serializers.ModelSerializer):
    order_items = OrderItemserSerializer(many=True)
    class Meta:
        model= Order
        fields = '__all__'


