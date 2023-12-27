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
def product_inside(request,slug):

    sqp_id = request.GET.get('sqp_id',None)
    
    if sqp_id !=None:
        sqp = SizeQuantityPrice.objects.get(id=sqp_id)

    else:
        product = get_object_or_404(Product,id =slug)
        sqp = product.sqp.first()

   


    product = get_object_or_404(Product,id =slug)

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
        'reviews':ReviewSerializer(Reviews.objects.filter(product=Product.objects.get(id=slug)),many=True).data,
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
    men_products = Product.objects.filter(gender='Men')
    women_products = Product.objects.filter(gender='Women')

    # Get distinct categories related to the filtered products
    men_categories = ProductCategory.objects.filter(products__in=men_products).distinct()
    women_categories = ProductCategory.objects.filter(products__in=women_products).distinct()

    # Serialize the data for categories
    category_data = category_serializer(men_categories, many=True).data
    women_category_data = category_serializer(women_categories, many=True).data

    # Add subcategories for each category
    for cat in category_data:
        category_instance = ProductCategory.objects.get(id=cat['id'])
        men_subcategories = ProductSubCategory.objects.filter(products__in=men_products, category=category_instance).distinct()
        cat['subcategories'] = subcategory_serializer(men_subcategories, many=True).data

    for cat in women_category_data:
        category_instance = ProductCategory.objects.get(id=cat['id'])
        women_subcategories = ProductSubCategory.objects.filter(products__in=women_products, category=category_instance).distinct()
        cat['subcategories'] = subcategory_serializer(women_subcategories, many=True).data
        
        
    # Combine data and return the response
    response_data = {'men_category': category_data,'women_category_data':women_category_data}
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
    
    
    

from django.views.generic import View
import pandas as pd
from product.models import Product, ProductImages
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from openpyxl import Workbook
from django.utils import timezone

def convert_to_unaware_datetime(dt):
    if dt:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return None



class DownloadProductDetailsView(View):

    @method_decorator(csrf_exempt)  # Only for development, you might want to remove this in production
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        # Retrieve products (replace this with your actual query)
        products = Product.objects.all()

        # Create the Excel file
        excel_file = export_products_to_excel()

        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=exported_products.xlsx'

        return response
        

        return response
import pandas as pd
from io import BytesIO
from django.core.files import File
from openpyxl import Workbook

def export_products_to_excel():
    # Fetch all products
    products = Product.objects.all()

    # Create a DataFrame with the product details
    data = []
    for product in products:
        for sqp in product.sqp.all():
            row = {
                'Generic': product.id,
                'Article': sqp.id,
                'EAN code': sqp.ean_code,
                'Season': product.season,
                'Season code': product.season_code,
                'COLOR': product.color,
                'MRP': product.mrp,
                'SLEEVE': product.sleeve,
                'DESIGN/SURFACE': product.design_surface,
                'OCCASION': product.occasion,
                'Product Title': product.name,
                'FIT': product.fit,
                'NECK TYPE': product.neck_type,
                'Gender': product.gender,
                'FABRIC DETAILS': product.fabric_detail,
                'Washcare': product.Washcare,
                'Category': product.category.name if product.category else None,
                'Sub-Category': product.subcategory.name if product.subcategory else None,
                'Sub-Sub-Category': product.subsubcategory.name if product.subsubcategory else None,
                'Color Family': product.color_family.name if product.color_family else None,
                'SIZE': sqp.size,
                'inches': sqp.inches,
                'Length (cm)': sqp.length,
                'Width (cm)': sqp.width,
                'Weight (gm)': sqp.weight,
                'Stock Quantity': sqp.quantity,
                'Launch Date':product.launch_date if product.launch_date else None,
                'model_size':product.model_size if product.model_size else None,
                'is_enable':product.is_enable if product.is_enable else None,
                'MC Desc.':product.mc_desc if product.mc_desc else None,
                'Manufacturer name':product.manufacturer if product.manufacturer else None,
                'STYLE':product.style if product.style else None,
                'cm':sqp.centimeter
            }
            data.append(row)

    df = pd.DataFrame(data)

    # Create a BytesIO buffer to write the Excel file
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)

    # Save the buffer content to a Django File
    buffer.seek(0)
    excel_file = File(buffer)
    excel_file.name = 'exported_products.xlsx'

    # Save the file to your ExcelFile model or use it as needed
    # For example, you can save it to the database or return it in a Django view
    # excel_file.save()
    return excel_file


def upload(request):
    if request.method == 'POST':
        file = request.FILES['file']
        ExcelFile.objects.create(file=file).save()
    return redirect('products_dashboard')


@api_view(['GET'])
def colorfamily(request):
    return Response({'colors':ColourFamilySerializer(ColourFamily.objects.all(),many=True).data},status=status.HTTP_200_OK)

# @api_view(['GET'])
# def all_sqp(request):
#     return Response({'sqp':SizeQuantityPriceSerializer(SizeQuantityPrice.objects.all(),many=True).data},status=status.HTTP_200_OK)