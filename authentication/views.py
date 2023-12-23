from django.shortcuts import render, redirect,get_object_or_404,HttpResponseRedirect
from authentication.models import *
from product.models import *
from django.contrib.auth import authenticate, login
import random
from django.contrib.auth import logout
from django.views.decorators.http import require_GET
from functions import send_email_otp,send_email_reset_link
from django.contrib import messages
from django.db.models import Q
# from django.utils.timezone import datetime
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_protect
from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from dashboard.models import HomeBannerImages,HomeBannerScrolling
from product.models import Product,DiscountOnProducts
from product import serializers
from product.serializers import product_serializer
from dashboard.models import *
import paypalrestsdk
from django.db.models import Sum
from django.contrib.auth.hashers import check_password
from django.shortcuts import render, redirect
from taggit.models import Tag
from rest_framework.authtoken.models import Token
import requests
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .serializer import *
from SizeUpp import settings
from datetime import datetime
url = 'https://api.instashipin.com/api/v1/tenancy/authToken'
payload ={
    "api_key": 
        "6092655223372029e7404dc4"
    }
headers = {
        'Content-Type': 'application/json',
    }
response = requests.post(url, json=payload, headers=headers)
if response.status_code == 200:
        data = response.json()
        token = data['data']['response']['token_id']    
        settings.SHIPING_TOKEN = token


def checkDelivery(pincode): 
        
    url = 'https://api.instashipin.com/api/v1/courier-vendor/freight-calculator'
    payload = {
        "token_id": settings.SHIPING_TOKEN,
        "fm_pincode": "400075",
        "lm_pincode": pincode,
        "weight": "0.5",
        "payType": "PPD",
        "collectable": ""
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        data = response.json()
        deliveryCharges = data['data']['response']['total_freight']
        return deliveryCharges
    else:
        return None




@api_view(['GET'])
def validate_pincode(request,slug):
    
        
    url = 'https://api.instashipin.com/api/v1/courier-vendor/check-pincode'

    payload = {
        "token_id": settings.SHIPING_TOKEN,
        "pincode": slug,
      
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        data = response.json()
        message = data['data']['response']['message']
        return Response({'message':message},status=status.HTTP_200_OK)



def placeDelivery(order_id):
    order = Order.objects.get(id=order_id)
    url = 'https://api.instashipin.com/api/v1/courier-vendor/external-book'
    toatal_weight =0
    items = []
    for orderitem in order.order_items.all():
        sqp = SizeQuantityPrice.objects.get( id= orderitem.sqp_code) 
        toatal_weight = round(toatal_weight + float(sqp.weight),2)
        items.append(
        {
        "name": orderitem.product.name,
        "quantity": orderitem.quantity,
        "sku": orderitem.sqp_code,
        "unit_price": orderitem.mrp,
        "actual_weight": orderitem.size,
        "item_color": "",
        "item_size": orderitem.size,
        "item_category": "",
        "item_image": "",
        "item_brand": ""
        }
        )
    payload = {
        "token_id": settings.SHIPING_TOKEN,
        "auto_approve": "true",
        "order_number": order.id,
        "payment_method": order.payment_type,
        "discount_total": "0.00",
        "cod_shipping_charge": "00.00",
        "invoice_total": order.payment_amount,
        "cod_total": order.payment_amount,
        # "length": "10",
        # "breadth": "10",
        # "height": "10",
        "actual_weight": toatal_weight,
        "volumetric_weight": "0.50",
        "shipping": {
        "first_name": order.customer_name,
        # "last_name": "Kumar",
        "address_1": order.address_line_1,
        "address_2": order.address_line_2,
        "city": order.city,
        "state": order.state,
        "postcode": order.postal_code,
        "country": "India",
        "phone": order.customer_contact,
        "cust_email": order.customer_email
        },
        "line_items": items,
        
        
        
        "pickup": {
        "vendor_name": "Test Vendor",
        "address_1": "Demo Address, do not pick",
        "address_2": "",
        "city": "Gurgaon",
        "state": "Haryana",
        "postcode": "122016",
        "country": "India",
        "phone": "8104739401"
        },
        "rto": {
        "vendor_name": "Test Vendor",
        "address_1": "Do not pick",
        "address_2": " ",
        "city": "Gurgaon",
        "state": "Haryana",
        "postcode": "122016",
        "country": "India",
        "phone": "8104739401"
        },
        "gst_details": {
        "gst_number": "",
        "cgst": "",
        "igst": "",
        "sgst": "",
        "hsn_number": "",
        "ewaybill_number": ""
        }
            
            }
    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        # Request was successful
        data = response.json()
        airwaybilno = data['data']['response']['airwaybilno']
        courier = data['data']['response']['courier']
        dispatch_label_url = data['data']['response']['dispatch_label_url']
        return airwaybilno,courier,dispatch_label_url
    
    
    
@api_view(['GET','POST'])
def home(request):
    if request.method == 'POST':
        email =request.data.get('email')
        if request.user.is_authenticated:
            
            if request.user.newsletter == True:
                message='Already Subscribed to Newsletter!!'
                return Response({'message':message},status=status.HTTP_400_BAD_REQUEST)

            elif request.user.email == email:
                user = User.objects.get(email=email)
                user.newsletter =True
                user.save()
                message='Thank You Subscribing to Our Newsletter'
                return Response({'message':message},status=status.HTTP_200_OK)


            elif Newsletter.objects.filter(email=email).exists():
                            message='Already Subscribed to Newsletter !!'
                            return Response({'message':message},status=status.HTTP_400_BAD_REQUEST)

            else:
                Newsletter.objects.create(email=email).save()

                message='Thank You Subscribing to Our Newsletter'
                return Response({'message':message},status=status.HTTP_200_OK)
            
        else:
                    return Response({'message':"Authentication Required"},status=status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED)


    products = Product.objects.all().order_by('created_at').reverse()[:10]
    serializer = serializers.product_serializer(products,many=True)
    products=serializer.data

    sale_on_product = DiscountOnProducts.objects.filter(active=True).order_by('created_at').reverse()[:2]


    #topselling products 
    top_selling_products = Product.objects.filter(
        orderitem__isnull=False  # Only consider products that have associated order items
    ).annotate(
        total_quantity=Sum('orderitem__quantity')  # Calculate the total quantity sold
    ).order_by(
        '-total_quantity'  # Order by total quantity in descending order
    )[:12]
    
    cntx={
        'title': 'Size Upp | Home',
        'img':HomeBannerImages.objects.first(),
        'images':HomeBannerScrolling.objects.all(),
        'products':products,
        'sale_on_product':sale_on_product,
        'top_selling_products':top_selling_products
    }
    return Response( cntx,status=status.HTTP_200_OK)


@csrf_protect
@api_view(['POST'])
def signup(request):
    if request.user.is_authenticated:
        return Response( status=status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED)
    
    else:
        if request.method == 'POST':
            first_name = request.data.get('first_name')
            last_name = request.data.get('last_name')
            email = request.data.get('email')
            phone = request.data.get('phone')
            password1 = request.data.get('password')
            newsletter = request.data.get('newsletter')
            # newsletter = True/False
            if newsletter == "on":
                newsletter = True
            else:
                newsletter = False

            if not email  or not phone or not password1:
                message='Require fileds'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(username=email).exists():
                message='Email Alrady Registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(email=email).exists():
                message='Email Alrady Registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            
            if User.objects.filter(phone=phone).exists():
                message='Phone numeber is already registered !!'
                return Response( {'message':message},status=status.HTTP_208_ALREADY_REPORTED)
            

            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=email,
                phone=phone,
                newsletter=newsletter,
            )
            user.set_password(password1)
            user.save()
            user = authenticate(request, username=email, password=password1)

            login(request, user)

            token, created = Token.objects.get_or_create(user=user)

            return Response({
                        'message': 'Login successful.',
                        'user_verified': user.is_verified,
                        'token': token.key,  # Include the token in the response
                    }, status=status.HTTP_200_OK)

        else:
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
        

        
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    if request.user.is_authenticated:
        Token.objects.get(user=request.user).delete()
        logout(request)
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_protect
@api_view(['POST'])
def signin(request):
        if request.user.is_authenticated:
            return redirect('home')     
        
        if request.method == 'POST':
            email = request.data.get('email')
            password = request.data.get('password')
            
            try:    
                user = User.objects.get(email=email)
                if check_password(password, user.password):
                    login(request, user)
                    token, created = Token.objects.get_or_create(user=user)

                    return Response({
                        'message': 'Login successful.',
                        'user_verified': user.is_verified,
                        'token': token.key,  # Include the token in the response
                    }, status=status.HTTP_200_OK)
                else:
                        return Response({'message': 'Invalid Password.'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                        
                        return Response({'message': 'Email Not Exist.'}, status=status.HTTP_400_BAD_REQUEST)
      


@api_view(['POST'])
def forgot_password(request):
    

    if request.method == 'POST':
        email = request.data.get('email')
        pass1 = request.data.get('password')


        # Check if the user exists
        if  User.objects.filter(email=email).exists():
            return Response({'message': 'Email Exist'}, status=status.HTTP_200_OK)
        

        else:
            # Handle the case where the user does not exist
            message='Email Not Exist!!'
            return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
     
    # If it's a GET request, render the empty form


@api_view(['POST','GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def otp(request):
    if request.user.is_authenticated:
        if request.user.is_verified :   
            return Response({'message': 'Verified','user_verified':request.user.is_verified}, status=status.HTTP_200_OK)

            
    if not request.user.is_verified:

        email = request.user.email
        user = User.objects.get(email=email)
        
        if request.method == 'POST':
            otp = request.data.get('otp')
         
            otp = str(otp['1']) + str(otp['2'])+ str(otp['3']) + str(otp    ['4'])
            print("^^^^^^^^^^^^^^",otp)
            if int(user.otp) == int(otp):
                
                user.is_verified = True
                user.otp = ''
                user.save()

                login(request, user)
                return Response({'message': 'Verification Done','user_verified':user.is_verified}, status=status.HTTP_200_OK)
                            
            else:
                message="OTP Invalid"
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            
        if request.method == 'GET':  
            if user.otp == '':
                otp = random.randint(1000, 9999)
                user.otp = otp
                user.save()
                # send opt to email
                send_email_otp(user=user,otp=otp)
                return Response({'message': 'OTP sent on Email','user_email':user.email}, status=status.HTTP_200_OK)
            return Response({'message': 'OTP Already sent on Email','user_email':user.email}, status=status.HTTP_200_OK)


     
@api_view(['POST','GET'])
def otp_forgot_pass(request):
        
        email = request.data.get('email')
        pass1 = request.data.get('password')
        user = User.objects.get(email=email)

        
        
        if request.method == 'POST':
            otp_ = request.data.get('otp')
            print("*************",otp_)
            otp1 = request.data.get('otp1')
            otp2 = request.data.get('otp2')
            otp3 = request.data.get('otp3')
            otp4 = request.data.get('otp4')
            otp = str(otp1) + str(otp2)+ str(otp3) + str(otp4)


            if user.otp == otp:
                user.is_verified = True
                user.otp = ''
                user.set_password(pass1)
                user.save()

                return Response({'message': 'Verification Done','user_verified':user.is_verified}, status=status.HTTP_200_OK)
                            
            else:
                message="OTP Invalid"
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            
        otp = random.randint(1000, 9999)
        user.otp = otp
        user.save()
        # send opt to email
        send_email_otp(user=user,otp=otp)
        message= 'OTP sent on email'
        return Response({'message': message}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def userprofile(request):
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif not request.user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':request.user.is_verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    
    
    print(Address.objects.filter(user=request.user))
    address = AddressSerializer(Address.objects.filter(user=request.user),many=True)
    orders = OrderserSerializer(Order.objects.filter(customer_email = request.user.email)[::-1],many =True)
    
    
    
    return Response({'title':'Profile','addresses':address.data,'orders':orders.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def address(request):
    user = User.objects.get(email=request.user.email)
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif not user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':user.is_verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    if request.method == 'POST':
            print(request.user.email)
            user = User.objects.get(id=request.user.id)
            address_line_1 = request.data.get('address_line_1')
            address_line_2 = request.data.get('address_line_2')
            city = request.data.get('city')
            postal_code = request.data.get('postal_code')
            country = request.data.get('country')
            state = request.data.get('state')
            is_default = request.data.get('is_default')
            if is_default == "on":
                    is_default = True
            else:
                    is_default = False

            addresses = Address.objects.filter(user=request.user)
            if is_default == True and addresses:
                for address in addresses:
                    address.is_default = False
                    address.save()


            address = Address.objects.create(
                user = user,
                address_line_1 = address_line_1,
                address_line_2 = address_line_2,
                city = city,
                postal_code = postal_code,
                country = country,
                state = state,
                is_default = is_default,
            )
            address.save()
            message= "Address Added Successfully"
            return Response({'message': message}, status=status.HTTP_200_OK)
    
    



@api_view(['PUT','DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])      
def address_by_id(request, id,slug):

    if not request.user.is_authenticated:
        return redirect('signin')
    
    elif not request.user.is_verified :
            request.session['signup_email'] = request.user.email
            return redirect('otp')
    
    if request.method == 'PUT':
                address_id = id
                address_line_1 = request.data.get('address_line_1')
                address_line_2 = request.data.get('address_line_2')
                state = request.data.get('state')
                city = request.data.get('city')
                country = request.data.get('country')
                postal_code = request.data.get('postal_code')
                is_default = request.data.get('is_default')
                if is_default == "on":
                    is_default = True
                else:
                    is_default = False
                address = Address.objects.get(id=address_id)
               
                addresses = Address.objects.filter(user=request.user)
                if is_default == True and addresses:
                    for old_address in addresses:
                        old_address.is_default = False
                        old_address.save()
                        
                address.address_line_1 = address_line_1
                address.address_line_2 = address_line_2
                address.city = city
                address.postal_code = postal_code
                address.country = country
                address.state = state
                address.is_default = is_default
                address.save()
                message= "Address Updated Successfully"
                return Response({'message': message}, status=status.HTTP_200_OK)
        
    
        
    if request.method == 'DELETE':
        address_id =id
        address = Address.objects.get(id=address_id)
        address.delete()
        return Response({'message': "Deleted Successfully"}, status=status.HTTP_200_OK)
    

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated]) 
def updateCart(request,slug):
    product = get_object_or_404(Product,id=slug)
    cart = Cart.objects.get(user=request.user,product=product)
    
    if request.method == 'POST':
        qty= request.data.get('qty',None)
        status_ = request.data.get('status')

        sqp_id = request.data.get('sqp_id',None)
        
        
        if status_:
            if status_ == 'add':
                cart.quantity = int(cart.quantity) + 1
            elif status_ == 'subtract':
                cart.quantity = int(cart.quantity) - 1
            
        if qty:
            
                cart.quantity = int(qty) 
            # if status_ == 'subtract':
        cart.save()
        cart.mrp = product.mrp
        cart.sub_total = round((float(cart.quantity)*float(cart.mrp)),2)
            
            # if product.discount == True:
            #     cart.discount_price = product.discounted_price
            #     cart.discount_percentage = product.discount_percentage
            #     cart.total_price =round((float(qty)*float(cart.discount_price)),2)   
        
        if sqp_id:
            sqp = SizeQuantityPrice.objects.get(id=sqp_id)
            cart.size_quantity_price = sqp
        # if selected_color:
        #     cart.color = selected_color
            
        cart.save()
        return Response({'message':'Cart is Updated'},status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def Add_Cart(request,slug):

    if request.user.is_authenticated:
        

        if request.method == 'POST':
            qty= request.data.get('qty',1)
            sqp_id = request.data.get('sqp_id')
            
        user = get_object_or_404(User,id=request.user.id)
        pro = get_object_or_404(Product,id=slug)
        size_quantity_price = get_object_or_404(SizeQuantityPrice,id=sqp_id)
        

        sub_total = (float(qty)*float(pro.mrp))
        
        
        
        # if pro.discount == True:
        #     discount_on_price = round(float(pro.price) - float(pro.discounted_price),2)
        #     total_price =round((float(qty)*float(pro.discounted_price)),2)
            
        # else: 
        #     discount_on_price = 0
        

        
        if Cart.objects.filter(user=request.user,product=pro).exists():
            return Response({'Message':'Already In Cart'},status=status.HTTP_208_ALREADY_REPORTED)
        cart_item = Cart.objects.create(user=user,product=pro,quantity=qty,size_quantity_price=size_quantity_price,mrp=pro.mrp ,sub_total=sub_total)
        
        
        cart_item.save()
    
        message="Added to cart"
        return Response({'message':message,'cart_id':cart_item.id},status=status.HTTP_201_CREATED)
   

        # if status == 'UPDATE':
        #     cart_item=Cart.objects.get(user=user,product=pro)

        #     cart_item.total_price = total_price
        #     cart_item.quantity = qty
        #     cart_item.save()
        #     messages.success(request,'Cart is Updated Successfully!!')
        #     return redirect('updateCart')

        # if Cart.objects.filter(user=user,product=pro):


        #     messages.error(request,"Already In cart")
        #     return redirect('product_inside',pro.id)





@api_view(['POST','GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def show_Cart(request):
    # try:
        if request.user.is_authenticated:
        
            cart_items = Cart.objects.filter(user=request.user)
            
            code=None
            
            # pincode = Address.objects.get(user=request.user,is_default=True).postal_code
            # if pincode:

            #         # deliveryCharges = checkDelivery(pincode)
            # else:
            deliveryCharges = 0
                    
            if request.method == 'POST':
                code = request.data.get('code')
                    
                if code and DiscountCoupon.objects.filter(code=code).exists():
                        
                    discountcoupon=DiscountCoupon.objects.get(code=code)
                    if discountcoupon.end_date > timezone.now():
                        coupon = 'active'
                    else: 
                        coupon = 'deactive'

                else:
                    coupon = 'deactive'
            else:
                coupon = 'deactive'
            
            products_list =[ ]
            total_price = 0
            mrp_price = 0
            sub_total=0
            discount_on_price = 0
            
            if cart_items.count() != 0:
                for item in cart_items:
                    mrp_price = round((mrp_price + (float(item.product.mrp)*int(item.quantity))),2)
                    
                    
                    sub_total = round(float(item.sub_total)+ sub_total, 2)
                    # if item.discount_on_price:
                    #     discount_on_price = discount_on_price + round((float(item.discount_on_price)*int(item.quantity)),2)
                    products_list.append({'qty':item.quantity,'cart':CartSerializer(item).data})
            else:
                return Response({'message':'Cart is Empty'},status=status.HTTP_400_BAD_REQUEST)  
            
            
            
            if coupon == 'active':
                if discountcoupon.percentage:
                    coupon_discount =  round(float(discountcoupon.percentage),2)*0.01
                if discountcoupon.price:
                    coupon_discount =  float(discountcoupon.price)

                cupon_discount = coupon_discount *sub_total
            else:
                cupon_discount = 0
            
            total_price = round(sub_total + float(deliveryCharges),2)
            if cupon_discount !=0:
                total_price = sub_total - round(coupon_discount *sub_total,2) 

                
            cntx={
                    'products':products_list,
                    'title':'My Cart',
                    'total_price':total_price,
                    'sub_total':sub_total,
                    'delivery_charges':deliveryCharges,
                    'coupon':coupon,
                    'cupon_discount':cupon_discount,
                    'mrp_price':mrp_price,
                    'discount_on_price':discount_on_price

                }

            
            return Response(cntx,status =status.HTTP_200_OK)
        
        
    # except Exception as e:
    #     return Response({"e":e}, status=status.HTTP_400_BAD_REQUEST)
            
@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def del_cart(request, slug):
    if request.user.is_authenticated:
        
        product = Product.objects.get(id=slug)
        if Cart.objects.filter(product=product,user= request.user).exists():
            cart = Cart.objects.get(product=product,user= request.user)
            cart.delete()
            message="Deleted"
        else:
            message = "Not Found"
        cart= CartSerializer(Cart.objects.filter(user=request.user),many=True).data
        return Response({'message':message,'cart':cart},status=status.HTTP_200_OK)
   



# def order(request):
#     if not request.user.is_authenticated:
#         return redirect('signin')
    
#     elif not request.user.is_verified :
#             request.session['signup_email'] = request.user.email
#             return redirect('otp')
    
#     if request.method == 'POST':
#             user = User.objects.get(id=request.user.id)
#             address_id = request.data.get('address_id')

#             payment_id = "Generated Using Stripe Here"

#             order = Order.objects.create(
#                 address_line_1 = address_id.address_line_1,
#                 address_line_2 = address_id.address_line_2,
#                 city = address_id.city,
#                 postal_code = address_id.postal_code,
#                 country = address_id.country,
#                 state = address_id.state,
#                 payment_id = payment_id,
#             )
#             order.save()

#             toatl_amount = 0
#             for item in Cart.objects.filter(user=user):
#                 order_item = OrderItem.objects.create(product=item.product,quantity=item.quantity,size_quantity_price=item.size_quantity_price)
#                 order.order_items.add(order_item)
#                 toatl_amount += item.size_quantity_price.price
#                 order.save()
                
#             return redirect('/')
    
#     else:
#         return render(request,'cart.html',{'title':'Cart'})




paypalrestsdk.configure({
    "mode": "sandbox",  # or "live"
    "client_id": "AW51S_03IaBs6Kc-6UqkuAqLq9VzcjASJtDuTtwJlHkZAOsjBuZI0qXiobIHptNyDkUFEFEY9mcE0APm",
    "client_secret": "EAq19jPmNnIL07UjfpfXow80Y_luf3Zubd6Z2U74duLn2zuqwS4FR0K-JDK9azi2d2dFy1Ht1SP3IkQ6"
})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def create_order(request):
        if request.method == 'POST':
            address_id = request.data.get('address_id')
           
            mrp_price = float(request.data.get('mrp_price', 0))
            sub_total = float(request.data.get('sub_total', 0))
            cupon_discount = float(request.data.get('cupon_discount', 0))
            total_price = float(request.data.get('total_price', 0))
            cupon_discount = float(request.data.get('cupon_discount',0))
            
            coupon = request.data.get('coupon',None)
            payment_type = request.data.get('payment_type','COD')
            
            
            
            if not address_id:
                message='Please Add/select Address'
                return Response({'message':message},status=status.HTTP_400_BAD_REQUEST)

            address = Address.objects.get(id=address_id)
            
            
            order = Order.objects.create(
                customer_name = request.user.first_name + '' + request.user.last_name,
                customer_email = request.user.email,
                customer_contact = request.user.phone,
                address_line_1 = address.address_line_1,
                address_line_2 = address.address_line_2,
                city = address.city,
                postal_code = address.postal_code,
                country = address.country,
                state = address.state,
                
                payment_type = payment_type,
                payment_status = "Pending",
                payment_id = None,
                payment_amount = None, 
            )        
            
            try :
                delivery_charges = checkDelivery(address.postal_code)
            except Exception as e:
                delivery_charges = 0

            order.payment_amount = total_price
            order.deliveryCharges = delivery_charges
            order.mrp_price = mrp_price            
            order.sub_total = round(sub_total,2)
            if coupon:
                order.cupon_discount = round(cupon_discount,2)
                
            order.coupon = coupon
            order.save()
            
            for cart in Cart.objects.filter(user=request.user):


                order_item = OrderItem.objects.create(
                        product = cart.product,
                        quantity = cart.quantity,
                        size = cart.size_quantity_price.size,
                        mrp = cart.mrp,
                        color = cart.product.color,
                        sub_total=cart.sub_total,
                        sqp_code=cart.size_quantity_price.id,
                    )
                # if cart.discount_price:
                #         discount_price = cart.discount_price
                # if cart.discount_percentage:
                #         discount_percentage=cart.discount_percentage
                        
                order_item.save()
                order.order_items.add(order_item)
                order.save()
                
                
                
                sqp = SizeQuantityPrice.objects.get(id=cart.size_quantity_price.id)
                sqp.quantity = int(sqp.quantity) - int(cart.quantity)
                sqp.save()
                
            if payment_type == 'COD':
                airwaybilno,courier,dispatch_label_url = placeDelivery(order.id)
                order.delivery_status= 'Order Processing'
                order.airwaybilno = airwaybilno
                order.courier = courier
                order.dispatch_label_url = dispatch_label_url
                return Response({'message':'Order Created'},status=status.HTTP_200_OK)
            
        
    #     payment = paypalrestsdk.Payment({
    #         "intent": "sale",
    #         "payer": {
    #             "payment_method": "paypal"
    #         },
    #         "redirect_urls": {
    #             "return_url": "http://127.0.0.1:8000/payment/execute/",
    #             "cancel_url": "http://127.0.0.1:8000/payment/cancel/"
    #         },
    #         "transactions": [{
    #             "amount": {
    #                 "total": total_price,
    #                 "currency": "USD"
    #             },
    #             "description": "Payment description"
    #         }]
    #     })
        
    #     if payment.create():
    #         request.session['paypal_payment_id'] = payment.id
    #         order.payment_id = payment.id
    #         order.save()
    #         for link in payment.links:
    #             if link.method == "REDIRECT":
    #                 redirect_url = str(link.href)
    #                 return redirect(redirect_url)
    #     else:
    #         messages.error(request,"Payment Canceled")
    #         return render(request, 'payment_error.html')
    # except Exception as e : 
    #     return Response({'message':e},status=status.HTTP_400_BAD_REQUEST)     


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def update_order(request,uuid):
    order = Order.objects.get(id=uuid)
    if order.payment_type != 'COD':
        
        payment_status = request.data.get('payment_status',None)
        payment_id = request.data.get('payment_id',None)
        # delivery_status = request.data.get('payment_status',None)
        # payment_status = request.data.get('payment_status',None)
        order.payment_status = payment_status
        order.payment_id = payment_id
        if payment_status == 'Completed':
            order.delivery_status = "Order Processing"

            #ship-delite integration
            
            
    return Response({'message':'Order Updated'},status=status.HTTP_200_OK)



def payment_execute(request):

    payment_id = request.session.get('paypal_payment_id')
    if payment_id is None:
        return redirect('home')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment:
        # Payment successful
        order = Order.objects.filter(payment_id=payment_id)[0]
        order_items = order.order_items.all()
        
        products = []
        for item in order_items:
            products.append(item.product)
            for sqp in item.product.size_quantity_price.all() :
                sqp = SizeQuantityPrice.objects.get(id = sqp.id)
                sqp.quantity = int(sqp.quantity) -int(item.quantity) 
                sqp.save()
                print(sqp.quantity,"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            
        serializer = product_serializer(products, many=True)

        order.payment_status = "Completed"
        order.delivery_status = "Order Processing"
        order.save()

        Cart.objects.filter(user=request.user).delete()

        cntx={
                    'payment':payment,
                    'products':serializer.data
        }
        # You can perform any additional actions here, such as updating your database
        messages.success(request,'Order Placed! You can check on order Track')
        return render(request, 'user_profile/order-success.html',cntx)
    else:
        # Payment failed
        order = Order.objects.filter(payment_id=payment_id)[0]
        
       
        order.payment_status = "Failed"
        order.save()

        messages.error(request,'Order Not Placed!')

        return render(request, 'payment_error.html')

def payment_cancel(request):
    # Payment cancelled
    order = Order.objects.filter(payment_id=payment_id)[0]
        
       
    order.payment_status = "Failed"
    order.save()
    messages.error(request,'Payment Canceled!')

    return render(request, 'payment_cancel.html')








# Navigations pages
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def contactus(request):
    if request.method == 'POST':
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone_number =request.data.get('phone_number')
        issue = request.data.get('issue')
        message = request.data.get('message')

        enquiry = SupportTickets.objects.create(name=first_name, email=email,number=phone_number,issue=issue,
                                        message=message)
        enquiry.save()
        message='Support Tickets Generated Successfully'
        return Response({'message':message},status=status.HTTP_200_OK)
        
    


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def wishlist(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(user=request.user)
        print("wishlist",wishlist)
        cart_items_lis = Cart.objects.filter(user=request.user)

        cart_items=[]
        if wishlist:
            for item in wishlist:
                for citem in cart_items_lis:
                    pro = get_object_or_404(Product,id=item.product.id)
                    product =product_serializer(pro).data
                    if citem.product.id == item.product.id:
                        product['cart'] = True
                    else:
                        product['cart'] = True
                    cart_items.append(product)
        cntx={
                'wishlist':cart_items,
            }
        return Response(cntx,status=status.HTTP_200_OK)

    


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])    
def add_wishlist(request,slug):
    if request.user.is_authenticated:
        try:
            pro = get_object_or_404(Product,id=slug)
            WishList.objects.create(user=request.user,product=pro).save()

            return Response({'message':"Added to wishlist"},status=status.HTTP_200_OK)
        except:
             message='Already in wishlist'
             return Response({'message':message},status=status.HTTP_208_ALREADY_REPORTED)

    else:
        return redirect('signin')


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  
def remove_wishlist(request,slug):
     if request.user.is_authenticated:
        product = get_object_or_404(Product,id=slug)
        if WishList.objects.filter(product=product).exists():
            WishList.objects.get(product=product).delete()

        wishlist = WishListSerializer(WishList.objects.filter(user=request.user),many=True).data
        return Response({'wishlist':wishlist},status=status.HTTP_200_OK)
        



def Track_order(request):
     if not request.user.is_authenticated:
            return redirect('signin')
     
     id = request.GET.get('id')
     if id:
            order = Order.objects.get(id=id)
     else:       
        try:
             
            order = Order.objects.filter(user=request.user).order_by('-id')[0]
        except :
             order =None

     return render(request,"user_profile/order-tracking.html",{'title':'Order Tracking','order':order})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])  
def Update_Profile(request):
    if  request.method == 'POST':
         first_name = request.data.get('first_name')
         last_name = request.data.get('last_name')
         contact = request.data.get('contact')
         gender = request.data.get('gender')
         new_email =request.data.get('new_email')
         user = User.objects.get(id = request.user.id)

         
         
         if User.objects.filter(phone=contact).exists():
                message = 'Phone numeber is already registered !!'
                return Response({"message":"Mobile Number Already Register"},status=status.HTTP_400_BAD_REQUEST)


         user.first_name = first_name
         user.last_name = last_name
         user.phone = contact
         user.gender = gender
         user.save()

         if new_email:
                if User.objects.filter(email=new_email).exists():
                    message='Email Alrady Registered !!'
                    return Response({'message':message},status=status.HTTP_400_BAD_REQUEST)
                
                user.email = new_email
                user.is_verified = False

                user.save()
                
                return Response({'message':"Profile Updated",'user_verified':request.user.is_verified},status=status.HTTP_200_OK)

         return Response({'message':"Profile Updated"},status=status.HTTP_200_OK)

    
          
         



def return_product(request):
     order_id = request.GET.get('id')
     order =Order.objects.get(id = order_id)
     if request.method == 'POST':
            order_id = request.GET.get('id')
            issue = request.data.get('issue')
            feedback =request.data.get('feedback')
            order = Order.objects.get(id =order_id)
            if ReturnOrders.objects.filter(order = order).exists():
                messages.error(request,"Return Order Already Initiated !!")
                return redirect('userprofile')
            else:
                 order.order_return = True
                 order.delivery_status = 'Cancel'
                 order.save()
                 ReturnOrders.objects.create(
                      order =order,
                      issue=issue,
                      feedback =feedback
                 ).save()
                 messages.success(request,"Return Order Initiated !!")
                 return redirect('userprofile')

     return render(request,'user_profile/return_product.html',{'title':'Return Product','order':order})
