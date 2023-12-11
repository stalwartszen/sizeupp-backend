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
from django.core.mail import send_mail
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
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

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
        
@require_GET
@api_view(['GET'])
def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
    else:
        return Response({'message': 'User is not authenticated.'}, status=status.HTTP_401_UNAUTHORIZED)


@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
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
        pass1 = request.data.get('pass1')
        pass2 = request.data.get('pass2')


        # Check if the user exists
        try:
            user = User.objects.get(email=email)
            if pass1 != pass2:
                 messages.error(request,'Password is  not matching !')
                 
            request.session['new_pass']={'email':email,'password':pass1}
            return Response({'message': 'Email Exist'}, status=status.HTTP_200_OK)
        

        except User.DoesNotExist:
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
            return Response({'message': 'Verified','user_verified':user.is_verified}, status=status.HTTP_200_OK)

            
    if not request.user.is_verified:

        email = request.user.email
        user = User.objects.get(email=email)
        
        if request.method == 'POST':
            otp = request.data.get('otp')
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
            otp = random.randint(100000, 999999)
            user.otp = otp
            user.save()
            # send opt to email
            send_email_otp(user=user,otp=otp)
            return Response({'message': 'OTP sent on Email','user_email':user.email}, status=status.HTTP_200_OK)


     
@api_view(['POST'])
def otp_forgot_pass(request):
        email = request.session['new_pass']['email']
        new_password = request.session['new_pass']['password']
        del request.session['new_pass']
        
        user = User.objects.get(email=email)

        
        
        if request.method == 'POST':
            otp = request.data.get('otp')


            if user.otp == otp:
                user.is_verified = True
                user.otp = ''
                user.set_password(new_password)
                user.save()

                return Response({'message': 'Verification Done','user_verified':user.is_verified}, status=status.HTTP_200_OK)
                            
            else:
                message="OTP Invalid"
                return Response({'message': message}, status=status.HTTP_400_BAD_REQUEST)
            
        otp = random.randint(100000, 999999)
        user.otp = otp
        user.save()
        # send opt to email
        send_email_otp(user=user,otp=otp)
        message= 'OTP sent on email'
        return Response({'message': message}, status=status.HTTP_200_OK)


@api_view(['GET'])
def userprofile(request):
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif not request.user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':request.user.is_verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    address = Address.objects.filter(user=request.user.id)
    orders = Order.objects.filter(customer_email = request.user.email)[::-1]
    return Response({'title':'Profile','addresses':address,'orders':orders}, status=status.HTTP_200_OK)


@api_view(['POST'])
def address(request):
    if not request.user.is_authenticated:
        return Response({'message':'Login Required'}, status=status.HTTP_400_BAD_REQUEST)
    
    elif not request.user.is_verified :
            return Response({'message':'Email Not Verified','user_verified':request.user.verified}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
    
    if request.method == 'POST':
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
    
    


      
def address_by_id(request, id,slug):

    if not request.user.is_authenticated:
        return redirect('signin')
    
    elif not request.user.is_verified :
            request.session['signup_email'] = request.user.email
            return redirect('otp')
    
    if slug == 'UPDATE':
        address_id = id
        if request.method =="POST":    
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
                messages.success(request,"Address Updated Successfully")
                return redirect('userprofile')
        
        else:
            address = Address.objects.get(id=address_id)
            return render(request,'update_forms/address_crud.html',{'title':'Update Address','address':address})
        
    elif slug == 'delete':
        address_id =id
        address = Address.objects.get(id=address_id)
        address.delete()
        return redirect('userprofile')
    

def updateCart(request):
   
    return redirect('show_cart')



def Add_Cart(request,uuid,sqp_id):

    if request.user.is_authenticated:
        
        qty= request.GET.get('qty',1)

        if request.method == 'POST':
            qty= request.data.get('qty',1)
            selected_color = request.data.get('selected_color')

            
        status = request.GET.get('status',None)


        user = get_object_or_404(User,id=request.user.id)
        pro = get_object_or_404(Product,id=uuid)
        size_quantity_price = get_object_or_404(SizeQuantityPrice,id=sqp_id)
        

        total_price = (float(qty)*float(size_quantity_price.price))
                    
        if size_quantity_price.discount:
            total_price =(float(qty)*float(size_quantity_price.discounted_price))
 

        if status == 'UPDATE':
            cart_item=Cart.objects.get(user=user,product=pro)

            cart_item.total_price = total_price
            cart_item.quantity = qty
            cart_item.save()
            messages.success(request,'Cart is Updated Successfully!!')
            return redirect('updateCart')

        if Cart.objects.filter(user=user,product=pro):


            messages.error(request,"Already In cart")
            return redirect('product_inside',pro.id)
        

        

        cart_item = Cart.objects.create(user=user,product=pro,quantity=qty,size_quantity_price=size_quantity_price,total_price=total_price)
        if selected_color :
                cart_item.color=selected_color
        else:
             selected_color = size_quantity_price.color
        cart_item.save()
    
        messages.success(request,"Added to cart")
        return redirect('updateCart')
    else:
        return redirect('signin')


def show_Cart(request):
    if request.user.is_authenticated:
    
        cart_items = Cart.objects.filter(user=request.user)
        code=None
        if request.method == 'POST':
            code = request.data.get('code')
            status= request.data.get('status')
            if code:
                if status =='apply':
                    discountcoupon=DiscountCoupon.objects.get(code=code)
                    dis_pro = discountcoupon.products.all()
                    coupon = 'activate'

        else:
                coupon = 'deactivate'
                dis_pro = []


        products_list =[ ]
        total_price = 0
        sub_total=0
        coupon_dis = 0
        if cart_items:
            for item in cart_items:
                product =get_object_or_404(Product,id=item.product.id)
                if product in dis_pro:
                     total_price = round((float(item.total_price)-(float(item.total_price) * (float(discountcoupon.percentage)/100))) + total_price, 2)
                     request.session[product.name] = {'price':round( float(item.total_price)-(float(item.total_price) * (float(discountcoupon.percentage)/100)) ,2)}
                     coupon_dis =  coupon_dis +(float(item.total_price) * (float(discountcoupon.percentage)/100))


                
                else:
                    total_price = round(float(item.total_price)+ total_price, 2)

                sub_total = round(float(item.total_price)+ sub_total, 2)

                products_list.append({'product':product,'qty':item.quantity,'sqp':item.size_quantity_price,'cart':item})

        
            cntx={
                'products':products_list,
                'title':'My Cart',
                'total_price':total_price,
                'sub_total':sub_total,
                'coupon_dis':coupon_dis,
                'coupon':coupon,

            }

        else:
            cntx={
                'title':'My Cart',
            }
        return render(request,'user_profile/cart.html',cntx)
    else:
         return redirect('signin')
            


def del_cart(request, uuid):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(id=uuid)
            cart.delete()
        except:
             product = Product.objects.get(id=uuid)
             cart = Cart.objects.get(product=product)
             cart.delete()
        messages.success(request,'')
        return redirect('show_cart')
    else:
         return redirect('signin')




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
def generate_serial_id(cls):
        # Get the current month and year as two-digit strings
        month = str(datetime.date.today().month).zfill(2)
        year = str(datetime.date.today().year)[-2:]

        # Calculate the next counting number
        last_serial_id = cls.objects.filter(
            serial_id__startswith=month + year
        ).order_by('-serial_id').first()

        if last_serial_id:
            last_count = int(last_serial_id.serial_id[-3:])
            new_count = last_count + 1
        else:
            new_count = 1

        # Create the new serial_id
        new_serial_id = f"{month}{year}-{str(new_count).zfill(3)}"

        return new_serial_id
def payment(request):
    address_id = request.GET.get('address')
    if not address_id:
        messages.error(request,'Please Add/select Address')
        messages.error(request,'To Add Addres: view Profile >> Address >> Add New Address')
        return redirect('checkout')

    address = Address.objects.get(id=address_id)

    order = Order.objects.create(
        customer_name = str(request.user.first_name +' ' +request.user.last_name),
        customer_email = request.user.email,
        customer_contact = request.user.phone,
        address_line_1 = address.address_line_1,
        address_line_2 = address.address_line_2,
        city = address.city,
        postal_code = address.postal_code,
        country = address.country,
        state = address.state,
        
        payment_status = "Pending",
        payment_id = None,
        payment_amount = None, 
    )


    order.serial_id = generate_serial_id(Order)
    order.save()
    total = float(request.GET.get('total_amount'))
    charge = float(request.GET.get('charge'))
    
    deliverycountry =request.GET.get('deliverycountry') 


    for item in Cart.objects.filter(user=request.user):

        color = item.color
        size = item.size_quantity_price.size
        price = item.size_quantity_price.price
        sqp_code = item.size_quantity_price.name
        quantity = item.quantity
        dropdown_size = item.dropdown_size

        total_price =  (float(quantity)*float(price)) 



        order_item = OrderItem.objects.create(
                product = item.product,
                quantity = quantity,
                color = color,
                size = size,
                price = price,
                total=total_price,
                sqp_code=sqp_code,
                dropdown_size=dropdown_size
            )
        order_item.save()
        order.order_items.add(order_item)


        order.payment_amount = total
        order.deliveryCountry = deliverycountry
        order.deliveryCharges = charge
        order.sub_total = round(float(total-charge),2)
        order.save()

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://127.0.0.1:8000/payment/execute/",
            "cancel_url": "http://127.0.0.1:8000/payment/cancel/"
        },
        "transactions": [{
            "amount": {
                "total": total,
                "currency": "USD"
            },
            "description": "Payment description"
        }]
    })
    
    if payment.create():
        request.session['paypal_payment_id'] = payment.id
        order.payment_id = payment.id
        order.save()
        for link in payment.links:
            if link.method == "REDIRECT":
                redirect_url = str(link.href)
                return redirect(redirect_url)
    else:
        messages.error(request,"Payment Canceled")
        return render(request, 'payment_error.html')


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
def contactus(request):
    if request.method == 'POST':
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        phone_number =request.data.get('phone_number')
        issue = request.data.get('issue')
        product = request.data.get('product',None)
        message = request.data.get('message')

        enquiry = SupportTickets.objects.create(name=first_name, email=email,number=phone_number,issue=issue,
                                         product=product,message=message)
        enquiry.save()
        messages.success(request,'Support Tickets Generated Successfully')
        return redirect('contactus')
        
    if  request.GET.get('id'):
        id=request.GET.get('id')
        order =Order.objects.get(serial_id=id)
    else:
         order =None
    return render(request,'navigation_pages/contact-us.html',{'title':'Help Desk','order':order})


def aboutus(request):
    reviews = Reviews.objects.all()[::-1]

    page = request.GET.get('page', 1)  # Get the current page number from the request

    paginator = Paginator(reviews, 4)  # Paginate the serialized data with 10 items per page
    try:
        reviews = paginator.page(page)
    except PageNotAnInteger:
        reviews = paginator.page(1)
    except EmptyPage:
        reviews = paginator.page(paginator.num_pages)   

    return render(request,'navigation_pages/about-us.html',{'title':'About Us','reviews':reviews})

def faq(request):
    return render(request,'navigation_pages/faq.html',{'title':'F&Q'})

def wishlist(request):
    if request.user.is_authenticated:
        wishlist = WishList.objects.filter(user=request.user)
        cart_items_lis = Cart.objects.filter(user=request.user)

        product_list = []
        cart_items=[]
        if wishlist:
            for item in wishlist:
                for citem in cart_items_lis:
                    if citem.product.id == item.product.id:
                        cart_items.append(item.product.id)

                pro = get_object_or_404(Product,id=item.product.id)
                product_list.append({'pro':pro})
            cntx={
                'product_list':product_list,
                'cart_items':cart_items,
                'title':"Wishlist"
            }
            return render(request,'user_profile/wishlist.html',cntx)
        else:

            return render(request,'user_profile/wishlist.html',{'title':'WishList'})

    else:
        return redirect('signin')


def add_wishlist(request,uuid):
    if request.user.is_authenticated:
        try:
            pro = get_object_or_404(Product,id=uuid)
            WishList.objects.create(user=request.user,product=pro).save()

            return redirect('wishlist')
        except:
             messages.error(request, 'Already in wishlist')
             return redirect('wishlist')

    else:
        return redirect('signin')


def remove_wishlist(request,uuid):
     if request.user.is_authenticated:
        try:
            product = get_object_or_404(Product,id=uuid)
            WishList.objects.get(product=product).delete()
        except Exception as e:
             print(e)
        return redirect('wishlist')
     else:
            return redirect('signin')



def Track_order(request):
     if not request.user.is_authenticated:
            return redirect('signin')
     
     id = request.GET.get('id')
     if id:
            order = Order.objects.get(serial_id=id)
     else:       
        try:
             
            order = Order.objects.filter(user=request.user).order_by('-id')[0]
        except :
             order =None

     return render(request,"user_profile/order-tracking.html",{'title':'Order Tracking','order':order})


def terms_condition(request):
     return render(request,"navigation_pages/Terms&condition.html",{'title':'Terms & Conditions'})

def articles(request):
     tag = request.GET.get('tag')
     query = request.GET.get('query')
     print(tag,query)
     
     if query:
        # If a query parameter is present, filter articles based on the query
        articles = Articles.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query)
        )
     elif tag:
        # If a tag parameter is present, retrieve the tag and filter articles based on the tag
        articles = Articles.objects.filter(tags__name__in=[tag])

        print(articles)
     else:
        # If neither query nor tag parameter is present, retrieve all articles
        articles = Articles.objects.all()

     tags =Tag.objects.all()
     top_selling_products = Product.objects.filter(
        orderitem__isnull=False  # Only consider products that have associated order items
    ).annotate(
        total_quantity=Sum('orderitem__quantity')  # Calculate the total quantity sold
    ).order_by(
        '-total_quantity'  # Order by total quantity in descending order
    )[:4]
     return render(request,"navigation_pages/blogs.html",{'articles':articles,'tags':tags,'top_selling_products':top_selling_products})


def article_details(request,id):
     article = Articles.objects.get(id=id)
     top_selling_products = Product.objects.filter(
        orderitem__isnull=False  # Only consider products that have associated order items
    ).annotate(
        total_quantity=Sum('orderitem__quantity')  # Calculate the total quantity sold
    ).order_by(
        '-total_quantity'  # Order by total quantity in descending order
    )[:4]
     articles = Articles.objects.all()
     tags =Tag.objects.all()

     return render(request,"navigation_pages/blog-details.html",{'title':article.name,'article':article,'top_selling_products':top_selling_products,'articles':articles,'tags':tags})




def Update_Profile(request):
    if  request.method == 'POST':
         first_name = request.data.get('first_name')
         last_name = request.data.get('last_name')
         contact = request.data.get('contact')
         gender = request.data.get('gender')
         new_email =request.data.get('new_email')
         user = User.objects.get(id = request.user.id)

         
         
         if User.objects.filter(phone=contact).exists():
                messages.error(request,'Phone numeber is already registered !!')
                return redirect('Update_Profile')


         user.first_name = first_name
         user.last_name = last_name
         user.phone = contact
         user.gender = gender
         user.save()

         if new_email:
                if User.objects.filter(email=new_email).exists():
                    messages.error(request,'Email Alrady Registered !!')
                    return redirect('Update_Profile')
                
                user.email = new_email
                user.is_verified = False

                user.save()
                
                return redirect('otp')

         return redirect('userprofile')
        
         
    cntx={
         'title':"Update Profile"
    }
    return render(request,'update_forms/update_profile.html',cntx)


def return_product(request):
     order_id = request.GET.get('id')
     order =Order.objects.get(serial_id = order_id)
     if request.method == 'POST':
            order_id = request.GET.get('id')
            issue = request.data.get('issue')
            feedback =request.data.get('feedback')
            order = Order.objects.get(serial_id =order_id)
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
