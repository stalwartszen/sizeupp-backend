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
from product.serializers import product_serializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from dashboard.models import *
# Create your views here.
def paginate_items(request,products):
    page = request.GET.get('page', 1)  # Get the current page number from the request

    paginator = Paginator(products, 16)  # Paginate the serialized data with 10 items per page
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)   
     
    return products
    


# get cart itms and wishlist items -----------------------

def get_items(request,allproducts):
    if request.user.is_authenticated:
        data=[]
        cart = Cart.objects.filter(user=request.user)
        cart_products = []

        wishlist = WishList.objects.filter(user=request.user)
        wishlist_products = []

        discounts = DiscountOnProducts.objects.all()
        dis_pro = []

        for product in discounts:
            for pro in product.products.all():
                dis_pro.append(pro) 

        for product in wishlist:
            wishlist_products.append(product.product)

        for product in cart:
            cart_products.append(product.product)

        
        for product in allproducts:
            serializer = product_serializer(product)
            details = serializer.data

            if product in cart_products:
                details["cart"] = True
            else:
                details["cart"] = False

            if product in wishlist_products:
                details["wishlist"] = True
            else:
                details["wishlist"] = 'False'

            if product in dis_pro:
                details['discount'] = DiscountOnProducts.objects.order_by('created_at').filter(products__name=product)[0]
            else:
                details['discount'] = False
            data.append(details)

    else:
        serializer = product_serializer(allproducts,many=True)
        data =serializer.data

    return data






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


def product_inside(request,uuid):

    sqp_id = request.GET.get('sqp_id',None)
    
    if sqp_id !=None:
        sqp = SizeQuantityPrice.objects.get(id=sqp_id)

    else:
        product = get_object_or_404(Product,id =uuid)
        sqp = product.size_quantity_price.first()

    try:
        dropdown_color = list(sqp.color.split(','))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",sqp.color,dropdown_color[1])

    except:
        dropdown_color=None


    product = get_object_or_404(Product,id =uuid)

    serializer = product_serializer(product)
    pro = serializer.data


    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        cart_products = []

        wishlist = WishList.objects.filter(user=request.user)
        wishlist_products = []

        for product in wishlist:
            wishlist_products.append(product.product.id)

        for product in cart:
            cart_products.append(product.product.id)

        if main_uuid.UUID(pro['id']) in cart_products:
            pro["cart"] = True
        else:
            pro["cart"] = False

        if main_uuid.UUID(pro['id']) in wishlist_products:
            pro["wishlist"] = True
        else:
            pro["wishlist"] = False   

    else:
            pro["cart"] = False
            pro["wishlist"] = False   
    
   

    pro['product_images'] = ProductImages.objects.filter(products__id =pro['id'])
    

    if request.user.is_authenticated:
        if Order.objects.filter(user=request.user,order_items__product=Product.objects.get(id=uuid)).exists():
            order = Order.objects.filter(user=request.user,order_items__product=Product.objects.get(id=uuid))
        else: 
            order=None
    else:
            order =None
    cntx={
        'pro':pro,
        'title':pro['name'],
        'sqp_active':sqp,
        'sqp_active_id':str(sqp.id),
        'product_images':pro['product_images'],
        'order':order,
        'reviews':Reviews.objects.filter(product=Product.objects.get(id=uuid)),
        'dropdown_color':dropdown_color,
        'related_products_category':Product.objects.filter(category__name=pro['category']['name']),
        'related_products_brand':Product.objects.filter(brand__name=pro['brand']['name'])
    }
    return render(request,'navigation_pages/product-inside.html',cntx)




def allproducts(request):

    if request.method == 'GET':
        minPrice = request.GET.get('minPrice')
        maxPrice = request.GET.get('maxPrice')

        if minPrice and maxPrice:
            minPrice = float(minPrice)
            maxPrice = float(maxPrice)

            products = Product.objects.filter(
                Q(size_quantity_price__price=maxPrice) 
            ).distinct()
            price = f'Price: ${minPrice} - ${maxPrice}'
        else:
            products = Product.objects.all()[::-1]
            price = None



    data = get_items(request,products)
    data = paginate_items(request,data)
    cntx={
        'data':data,
        'title':'Products',
        
        'price':price,
        'colors' :ColourFamily.objects.all()
    }
    return render(request,"navigation_pages/allproducts.html",cntx)


#Category API
def cat_list(request):
    cats= ProductCategory.objects.all().distinct()
    nav_cat_list={}
    for cat in cats:
        subcat = ProductSubCategory.objects.filter(category__name=cat)
        if subcat:
            
            nav_cat_list[cat.name]=list(subcat.values())
        else:
            nav_cat_list[cat.name]=[dict({'category_id':cat.id})]



    return JsonResponse(nav_cat_list)




# Filters --------------------------------------------

def Color_Filter(request,slug):
        if request.method == 'GET':
            minPrice = request.GET.get('minPrice')
            maxPrice = request.GET.get('maxPrice')

        if minPrice == None or maxPrice== None:
                products = Product.objects.filter(size_quantity_price__color_family__name = slug).distinct()
                price =None

        else:
                products = Product.objects.filter(
                            Q(size_quantity_price__price__lt=maxPrice) & Q(size_quantity_price__price__gt=minPrice),
                            size_quantity_price__color_family__name = slug
                        ).distinct()
                price = f'Price: ${minPrice} - ${maxPrice}'

        data = get_items(request,products)
        data = paginate_items(request,data)

        cntx={
            'data':data,
            'title':'Products',
            'color':slug,
            'price':price,
            'colors': ColourFamily.objects.all()

        }
        return render(request,"navigation_pages/allproducts.html",cntx)




def cat_filter(request,slug):
    category = ProductCategory.objects.get(id=slug)

    if request.method == 'GET':
                subCat = request.GET.get('subCat',None)
                print("EE#############",subCat)
                if subCat:
                    products = Product.objects.filter(subcategory__name=subCat)
                else:
                    products = Product.objects.filter(category__name=category.name)

    data = get_items(request,products)
    data = paginate_items(request,data)

    colors = ColourFamily.objects.all()
    cntx={
        'data':data,
        'title':'Products',
        'colors':colors,
        'category':category.name
    }
        
    return render(request,"navigation_pages/allproducts.html",cntx)

def category(request,slug):
    category = ProductCategory.objects.get(name=slug)

    
    products = Product.objects.filter(category=category )

       
    data = get_items(request,products)
    data = paginate_items(request,data)

    colors = ColourFamily.objects.all()
    cntx={
        'data':data,
        'title':'Products',
        'colors':colors,
        'category':category.name
    }
        
    return render(request,"navigation_pages/allproducts.html",cntx)

def brand_filter(request,uuid):
    products = Product.objects.filter(brand__id = uuid)
    
    data = get_items(request,products)
    data = paginate_items(request,data)

    cntx={
            'data':data,
            'title':'Products',
            'Brand':Brand.objects.get(id=uuid).name,
            'colors' :ColourFamily.objects.all()

        }
    return render(request,"navigation_pages/allproducts.html",cntx)


def Discount_filter(request):
    try:
        discount_percentage= float(request.GET.get('discount'))
        print(discount_percentage)
        products = Product.objects.filter(
        Q(size_quantity_price__discount_percentage__lt=discount_percentage) &
        Q(size_quantity_price__discount=True)
    ).distinct()

        data = get_items(request,products)
        data = paginate_items(request,data)

        discount = f'{discount_percentage}%'
        cntx={
                'data':data,
                'title':'Products',
                'Discount':discount,
                'colors' :ColourFamily.objects.all()

            }
        return render(request,"navigation_pages/allproducts.html",cntx)
    except:
        return redirect('allproducts')
    



def Deal_filter(request,):



    products = Product.objects.filter(Q(discountonproducts__end_date__gt=timezone.now()) | Q(discountonproducts__active=True) | Q(size_quantity_price__discount = True)).distinct()
    
    # products = Product.objects.filter(Q(size_quantity_price__discount = True))
    
    data = get_items(request,products)
    data = paginate_items(request,data)

    cntx={
            'data':data,
            'title':'Products',
            'colors' :ColourFamily.objects.all()

        }
    return render(request,"navigation_pages/allproducts.html",cntx)




def Search(request):
    if request.method=='GET':
        query = request.GET.get('search')

    if query:
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))
            # You can add more fields to search by using additional Q objects
            # For example: Q(field_name__icontains=query) | Q(another_field__icontains=query)

           

        data = get_items(request,products)
        data = paginate_items(request,data)
        cntx={
                'data':data,
                'title':'Products',
                # 'Discount':discount,
                'colors' :ColourFamily.objects.all()

            }
        return render(request,"navigation_pages/allproducts.html",cntx)
    return render(request,"navigation_pages/allproducts.html",{'title':'Search','cntx':'Not Found'})


### ---- Payment Gateway ------------
def paymentGateway(request):
    address = request.GET.get('address')
    total = float(request.GET.get('total'))
    return redirect('success_page')

def success_page(request):
    return render(request,'user_profile/order-success.html')


def review_post(request,id):
    if request.method == 'POST':
        comment = request.POST.get('comment')
        review = Reviews.objects.create(user=request.user,product = Product.objects.get(id=id),comment=comment)
        review.save()
        messages.success(request,"Thank You For Feedback!")
    review_id =request.GET.get('review')
    if review_id:
        Reviews.objects.get(id=review_id).delete()
        messages.success(request,"Deleted Successfully")
        
    return redirect('product_inside',id)