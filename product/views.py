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






def Checkout(request):
    carts =Cart.objects.filter(user=request.user)
   
    addresses = Address.objects.filter(user=request.user)
    cart_list =[]
    sub_total = 0
    for item in carts:
            sub_total = round(float(sub_total) + float(item.total_price),2)
            serializer = product_serializer(item.product)
            product = serializer.data
            product['cart'] = item
            cart_list.append(product)


            
    delivery_charges = DeliveryCharges.objects.all()

    deliveryCharges = None
    if request.GET.get('Dcountry') != 'None' and request.GET.get('Dcountry'):
            did = request.GET.get('Dcountry')
            deliveryCharges = DeliveryCharges.objects.get(id=did)

            charge = deliveryCharges.charges
            total_amount = sub_total + charge

    else:
        total_amount = None
        charge = None


    # if sub_total > 100:
    #     charge =0
    #     total_amount = sub_total

        try:
            request.session.pop('Dcountry')
        except:
            pass

    cntx={
        'title':'checkout',
        'cart_list':cart_list,
        'addresses':addresses,
        'delivery_charges':delivery_charges,
        'total_amount':total_amount,
        'deliveryCharges':deliveryCharges,
        'charge':charge,
        'sub_total':sub_total

    }
    return render(request,'user_profile/checkout.html',cntx)






def Brands(request):
    brands = Brand.objects.all()
    brands_list =[]
    for br in brands:
        pro = Product.objects.filter(brand=br).count()
        brands_list.append({'brand':br,'pro':pro}) 
    cntx={
        'brands':brands_list,
        'title':'Brands'
    }
    return render(request,'navigation_pages/Brands-grid.html',cntx)

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
    cats= ProductDetailCategory.objects.all()
    

    serializer = detail_category_serializer(cats,many=True)


    return Response( {'detail_category':serializer.data},status=status.HTTP_200_OK)








### ---- Payment Gateway ------------
# def paymentGateway(request):
#     address = request.GET.get('address')
#     total = float(request.GET.get('total'))
#     return redirect('success_page')

# def success_page(request):
#     return render(request,'user_profile/order-success.html')

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def review_post(request,id):
    if request.method == 'POST':
        comment = request.data.get('comment')
        rating = float(request.data.get('rating'))
        review = Reviews.objects.create(user=request.user,product = Product.objects.get(id=id),comment=comment,rating=rating)
        review.save()
        message="Thank You For Feedback!"
        return Response({'message':message},status=status.HTTP_200_OK)
    