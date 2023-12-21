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





@api_view(['POST'])
def productfilter(request):
    try:
        if request.method == 'POST':
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
    except Exception as e :
        return Response({"message": e},status=status.HTTP_400_BAD_REQUEST)

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
    # Get all subcategories
    subcategories = ProductSubCategory.objects.order_by('-id').all()
    sub_category = []
    for subcat in subcategories:
        subcat_={
            'id':subcat.id,
            'name':subcat.name
        }
        detail_category=[]
        for detail_cat in ProductDetailCategory.objects.filter(subcategory=subcat):
            detail_category.append({'id':detail_cat.id,'name':detail_cat.name})    
        subcat_['detail_category']=detail_category
        sub_category.append(subcat_)
        

    # Get a list of category names
    categories = [{'name':category.name,'id':category.id} for category in ProductCategory.objects.order_by('-id').all()]

    # Combine data and return the response
    response_data = {'subcategories': sub_category,  'categories': categories}
    return Response(response_data, status=status.HTTP_200_OK)






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
    
    
    

from product.serializers import size_quantity_price_serializer
from django.views.generic import View
import pandas as pd
from product.models import Product, ProductImages
from django.http import HttpResponse

class ExportExcelView(View):
    def get(self, request):
        # Generate Excel file
        file_path = 'products.xlsx'
        export_products_to_excel(file_path)

        # Prepare response with Excel file
        with open(file_path, 'rb') as excel_file:
            response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=products.xlsx'

        return response

def export_products_to_excel(file_path='products.xlsx'):
    # Retrieve all products and related images
    products = Product.objects.all()
    images_data = []
    for product in products:
        for img in product.productimages_set.all():
            images_data.append({'product_id': product.id, 'image_url': img.img.url})

    # Create DataFrame
    product_df = pd.DataFrame(list(products.values()))
    images_df = pd.DataFrame(images_data)

    # Merge DataFrames on product_id
    merged_df = pd.merge(product_df, images_df, left_on='id', right_on='product_id', how='left')

    # Drop redundant columns
    merged_df = merged_df.drop(['id_y', 'product_id'], axis=1)

    # Save to Excel file
    merged_df.to_excel(file_path, index=False)



def upload(request):
    return redirect('products_dashboard')