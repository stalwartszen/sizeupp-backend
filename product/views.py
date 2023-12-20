from django.shortcuts import render,get_object_or_404,redirect
from django.http import JsonResponse
from .models import *
from authentication.models import *
import json
from django.utils import timezone
from authentication.serializer import CartSerializer
from django.contrib import messages
import uuid as main_uuid
from django.db.models import Q
from product.serializers import *
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from dashboard.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status


# get cart itms and wishlist items -----------------------





@api_view(['GET'])
def productfilter(request):
    category_id = request.data.get('category_id', None)
    sub_category_id = request.data.get('sub_category_id', None)
    colorfamily_id = request.data.get('colorfamily_id', None)
    price = request.data.get('price', None)
    search = request.data.get('search', None)
    discounted_products = request.data.get('discounted_products', None)
    
    products = Product.objects.all()

    if search:
        products = Product.objects.filter(
            Q(name__icontains=search) | 
            Q(description__icontains=search) | 
            Q(additional_info__icontains=search) |
            Q(category__name__icontains=search) | 
            Q(subcategory__name__icontains=search)
        )
        return Response({'products': product_serializer(products, many=True).data}, status=status.HTTP_200_OK)
    
    if category_id:
        products = products.filter(category__id=category_id)
    
    if sub_category_id:
        products = products.filter(subcategory__id=sub_category_id)
    
    if colorfamily_id:
        products = products.filter(color_family__id=colorfamily_id)
        
    if price:
        products = products.filter(price__lt=float(price))
        
    if discounted_products:
        products = products.filter(discount=True)
        
    return Response({'products': product_serializer(products, many=True).data}, status=status.HTTP_200_OK)


@api_view(['GET'])
def product_inside(request,uuid):

    sqp_id = request.GET.get('sqp_id',None)
    
    if sqp_id !=None:
        sqp = SizeQuantityPrice.objects.get(id=sqp_id)

    else:
        product = get_object_or_404(Product,id =uuid)
        sqp = product.sqp.first()

   


    product = get_object_or_404(Product,id =uuid)

    pro_serializer = product_serializer(product)

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart_products = []

        wishlist = WishList.objects.filter(user=request.user)
        wishlist_products = []

        for i in wishlist:
            wishlist_products.append(i.product.id)

        for i in cart:
            cart_products.append(i.product.id)

        print(cart_products,"***********************************")
        print(wishlist_products,"!!!!!!!!!!!!!!!!!!!!!")
        
        if product.id in cart_products:
            cart =True
        else:
            cart= False

        if product.id in wishlist_products:
            wishlist= True
        else:
            wishlist= False   

    else:
            cart= False
            wishlist= False   
    

    images = ProductImages.objects.filter(products =product)

    img_serializer = ProductImagesSerializer(images,many=True)
    
    cntx={
        'product':pro_serializer.data,
        'sqp_active':SizeQuantityPriceSerializer(sqp).data,
        # 'sqp_active_id':str(sqp.id),
        'cart':cart,
        'wishlist':wishlist,
        'product_images':img_serializer.data,
        # 'order':order,
        'reviews':ReviewSerializer(Reviews.objects.filter(product=Product.objects.get(id=uuid)),many=True).data,
        'related_products_category':product_serializer(Product.objects.filter(category=product.category),many=True).data,
    }
    return Response(cntx,status=status.HTTP_200_OK)


@api_view(['GET'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def allproducts(request):
    products = Product.objects.all()
    pro_list = product_serializer(products,many=True).data
    
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart_products = []

        wishlist = WishList.objects.filter(user=request.user)
        wishlist_products = []

        for product_i in wishlist:
            wishlist_products.append(product_i.product.id)

        for product_c in cart:
            cart_products.append(product_c.product.id)
        for pro in pro_list:
        
            if pro['id'] in cart_products:
                pro['cart'] =True
            else:
                pro['cart']= False

            if pro['id'] in wishlist_products:
                pro['wishlist']= True
            else:
                pro['wishlist']= False   

    return Response( pro_list,status=status.HTTP_200_OK)



#Category API
@api_view(['GET'])
def cat_list(request):
    serializer = detail_category_serializer(ProductDetailCategory.objects.order_by('-id').all(),many=True)
    category = [i.name for i in ProductCategory.objects.order_by('-id').all()]

    return Response( {'detail_category':serializer.data,'category':category},status=status.HTTP_200_OK)








@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def review_post(request):
    if request.method == 'POST':
        id = request.data.get('id')

        comment = request.data.get('comment')
        rating = float(request.data.get('rating'))
        review = Reviews.objects.create(user=request.user,product = Product.objects.get(id=id),comment=comment,rating=rating)
        review.save()
        message="Thank You For Feedback!"
        return Response({'message':message},status=status.HTTP_200_OK)
    