import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from authentication.models import *
from product.models import *
from django.contrib import messages
from product.serializers import product_serializer
from django.forms import formset_factory
from .models import *
from product.forms import *
from django.db.models import Sum, Count
from taggit.models import Tag
from taggit.utils import parse_tags
from django.db.models import Sum
from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from  .export  import export_products_to_excel
from product.serializers import SizeQuantityPriceSerializer,size_quantity_price_serializer

import json


def dashboard(request):
      if not request.user.is_authenticated:
        return redirect('dashboard_signin')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('home')
      


      products = Product.objects.all()[::-1]
      users =User.objects.filter(is_superuser= False)


      try:
            revenue = round(Order.objects.filter(payment_status='Completed').filter(delivery_status='Delivered').aggregate(total_revenue=Sum('payment_amount'))['total_revenue'],2)
      except:
            revenue = 0
      
      top_selling_products = Product.objects.annotate(
      order_count=Count('orderitem__product'),
      total_quantity=Sum('orderitem__quantity')
      ).order_by(
      '-order_count', '-total_quantity'
      )[:4]
            
      top_selling_products_list = []
      for i in top_selling_products:
            orders = Order.objects.filter(payment_status='Completed').filter(delivery_status='Delivered').filter(order_items__product__id = i.id).count()


            top_selling_products_list.append({'orders':orders,'product': i})


      orders = Order.objects.filter(delivery_status='Order Processing')[::-1][0:6]
      order_count =Order.objects.filter(payment_status='Completed').filter(delivery_status='Delivered').count()


      
      cntx={
            'revenue':revenue,
            "title":"Dashboard",
            "active":"dashboard",
            'orders':orders,
            'products':products,
            'users':users,
            'order_count':order_count,
            'todolist':TodoList.objects.filter(checked =False)[::-1],
            'top_selling_products_list':top_selling_products_list
      }
      return render(request, 'back-end/index.html', cntx)



def signin(request):
      if request.user.is_superuser:
            return redirect('dashboard')

      else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                messages.success(request,'Loged In')
                return redirect('dashboard')
            
            else:
                messages.error(request,'Not Allowed')
                return redirect('dashboard_signin')
            
      return render(request, 'back-end/login.html', {"title":"Dashboard- Signin","active":"dashboard_signin"})
        

def brand(request):
        if not request.user.is_authenticated:
            return redirect('dashboard')
        
        if not request.user.is_superuser:
            messages.error(request,"Not Allowed")
            return redirect('dashboard')
        slug = request.GET.get('slug')
        if slug == 'Add':
              if  request.method == 'POST':
                name= request.POST.get('brand_name')
                details= request.POST.get('details',None)
                address= request.POST.get('address',None)
                contact= request.POST.get('contact',None)
                

                if Brand.objects.filter(name=name).exists():
                        messages.error(request,"Brand Already Exist.")
                        return redirect('brand_dashboard')
                else:
                        Brand.objects.create(name=name,details=details,address=address,contact=contact).save()
                        messages.success(request,"Added Sucessfully")
                        return redirect('brand_dashboard')
              else:
                    return render(request,"back-end/add-new-brand.html",{"slug":'Add'})
     
        if slug == "Update":
                id = request.GET.get('id')
                if request.method=='POST':
                    name= request.POST.get('brand_name')
                    details= request.POST.get('details',None)
                    address= request.POST.get('address',None)
                    contact= request.POST.get('contact',None)
                    brand = Brand.objects.get(id=id)
                
                    
            
                    brand.name = name
                    brand.details = details
                    brand.address = address
                    brand.contact = contact
                    
                    brand.save()
                    messages.success(request,"Brand Updated Successfully")
                    return redirect('brand_dashboard')
                else:
                      brand = Brand.objects.get(id=id) 
                      return render(request,'back-end/add-new-brand.html',{'brand':brand})
                    
    
        if slug == 'Delete':
                id = request.GET.get('id')
                
                Brand.objects.get(id=id).delete()
                return redirect('brand_dashboard')

        
        brands = Brand.objects.all()[::-1]
        return render(request,'back-end/brands.html',{'title':'Brands','brands':brands})
    


def category(request):
        if not request.user.is_authenticated:
            return redirect('dashboard')
        
        if not request.user.is_superuser:
            messages.error(request,"Not Allowed")
            return redirect('home')
        
        
        categories = ProductCategory.objects.all()[::-1]
        return render(request,'back-end/category.html',{'title':'Add Category','categories':categories})
    


      
def category_crud(request):

    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser :
            return redirect('dashboard')

    slug = request.GET.get('slug')

    if slug == 'Add':
         brand_id= request.POST.get('brand_name')
         category_name= request.POST.get('category_name')
         brand = Brand.objects.get(id=brand_id)
         if category_name:
            if ProductCategory.objects.filter(name=category_name,brand=brand).exists():
                        pass
            else:
                        ProductCategory.objects.create(name=category_name,brand=brand).save()
         return redirect('category_dashboard')


    if slug == 'Update':
        category_id = request.GET.get('id')
        if request.method =="POST":    
                name = request.POST.get('category_name')
                brand_id= request.POST.get('brand_name')
                brand = Brand.objects.get(id=brand_id)

                category = ProductCategory.objects.get(id=category_id)
               
                
                category.brand= brand
                category.name = name
                category.save()
                messages.success(request,"Category Updated Successfully")
                return redirect('category_dashboard')
        
        else:
            category = ProductCategory.objects.get(id=category_id)
            brands = Brand.objects.all()[::-1]
            return render(request,'back-end/add-new-category.html',{'title':'Update Category','category':category,'brands':brands})
    



    elif slug == 'Delete':
        category_id = request.GET.get('id')

        category = ProductCategory.objects.get(id=category_id)
        category.delete()
        return redirect('category_dashboard')
    else:
         brands = Brand.objects.all()[::-1]
         categories = ProductCategory.objects.all()[::-1]
         subcategories = ProductSubCategory.objects.all()[::-1]
         return render(request,'back-end/add-new-category.html',{'title':'Update Category','brands':brands,'slug':'Add','categories':categories,'subcategories':subcategories})
    
    



def subcategory(request):
    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser :
            return redirect('dashboard')
    
    subcategories = ProductSubCategory.objects.all()[::-1] 
    return render(request,'back-end/subcategory.html',{'title':'Add Category','subcategories':subcategories})
    


      
def subcategory_by_id(request,):

    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser :
            return redirect('dashboard')
    
    slug = request.GET.get('slug')

    if slug == 'Add':
         if request.method =='POST':
            category_name,brand_name= request.POST.get('category_name').split(',')
            sub_category_name= request.POST.get('sub_category_name')


            category = ProductCategory.objects.get(name=category_name,brand__name=brand_name)

            if category_name:
                if ProductSubCategory.objects.filter(name=sub_category_name,category=category,category__brand = category.brand).exists():
                            pass
                else:
                            ProductSubCategory.objects.create(name=sub_category_name,category=category).save()
            return redirect('sub_category_dashboard')
         else:
                categories = ProductCategory.objects.all()[::-1] 
                return render(request,'back-end/add-new-sub-category.html',{'slug':'Add','categories':categories})


    if slug == 'Update':
        sub_category_id = request.GET.get('id')
        if request.method =="POST":    
                name = request.POST.get('sub_category_name')
                category_name,brand_name= request.POST.get('category_name').split(',')

                subcategory = ProductSubCategory.objects.get(id=sub_category_id)
               
                subcategory.category = ProductCategory.objects.get(name=category_name,brand__name=brand_name)

                subcategory.name = name
                subcategory.save()
                messages.success(request,"Category Updated Successfully")
                return redirect('sub_category_dashboard')
        
        else:
            subcategory = ProductSubCategory.objects.get(id=sub_category_id)
            categories = ProductCategory.objects.all()[::-1]
            return render(request,'back-end/add-new-sub-category.html',{'title':'Update Sub Category','subcategory':subcategory,'categories':categories})
    



    elif slug == 'Delete':
        category_id = request.GET.get('id')

        category = ProductSubCategory.objects.get(id=category_id)
        category.delete()
        return redirect('sub_category_dashboard')
    else:
         brands = Brand.objects.all() 
         categories = ProductCategory.objects.all()[::-1]
         subcategories = ProductSubCategory.objects.all()[::-1]
         return render(request,'back-end/add-new-category.html',{'title':'Update Category','brands':brands,'slug':'Add','categories':categories,'subcategories':subcategories})
    





def detail_category(request):
    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser :
            return redirect('dashboard')
    
    
    detailcategories = ProductDetailCategory.objects.all()[::-1] 
    return render(request,'back-end/Detailcategory.html',{'title':'Add Detail Category','detailcategories':detailcategories})


      
def detail_category_by_id(request,):

    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser :
            return redirect('dashboard')
    
    slug = request.GET.get('slug')

    if slug == 'Add':
         sub_category,category_name,brand_name= request.POST.get('sub_category_name').split(',')
         detail_category_name= request.POST.get('detail_category_name')
         sub_category = ProductSubCategory.objects.get(name=sub_category,category__name=category_name,category__brand__name=brand_name)
         if detail_category_name:
            if ProductDetailCategory.objects.filter(name=detail_category_name,subcategory=sub_category,subcategory__category=sub_category.category).exists():
                        pass
            else:
                        ProductDetailCategory.objects.create(name=detail_category_name,subcategory=sub_category).save()
         return redirect('detail_category_dashboard')


    if slug == 'Update':
        detail_category_id = request.GET.get('id')
        if request.method =="POST":    
                name = request.POST.get('detail_category_name')
                sub_category,category_name,brand_name= request.POST.get('sub_category_name').split(',')
                sub_category = ProductSubCategory.objects.get(name=sub_category,category__name=category_name,category__brand__name=brand_name)

                detailcategory = ProductDetailCategory.objects.get(id=detail_category_id)
               
                
                detailcategory.subcategory = sub_category  
                detailcategory.name = name
                detailcategory.save()
                messages.success(request,"Category Updated Successfully")
                return redirect('detail_category_dashboard')
        
        else:
            detailcategory = ProductDetailCategory.objects.get(id=detail_category_id)
            subcategory = ProductSubCategory.objects.all()[::-1] 
            return render(request,'back-end/add-new-detail-category.html',{'title':'Update Category','subcategory':subcategory,'detailcategory':detailcategory})
    



    elif slug == 'Delete':
        category_id = request.GET.get('id')

        category = ProductDetailCategory.objects.get(id=category_id)
        category.delete()
        return redirect('detail_category_dashboard')
    else:
         subcategories = ProductSubCategory.objects.all() 
         return render(request,'back-end/add-new-detail-category.html',{'title':'Update Category','slug':'Add','subcategories':subcategories})
    


def Products_dashboard(request):
     if not request.user.is_authenticated:
            return redirect('dashboard')
    
     if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
     
     products = Product.objects.all() .order_by('created_at')
     serializer =product_serializer(products,many=True)
     action = request.GET.get('action')


     if action== 'export':
          return export_products_to_excel(request,products)
     products = serializer.data

     cntx={
        'title':'All Products',
        'products':products[::-1]
     }

     return render(request,'back-end/products.html',cntx) 


def addproduct(request):
     
     if request.method == 'POST':
          
        product_name = request.POST.get('product_name')
        product_description = request.POST.get('product_description')
        brand_id = request.POST.get('brand_id')
        category_id = request.POST.get('category_id')
        subcategory_id = request.POST.get('subcategory_id')
        detail_category_id = request.POST.get('detail_category_id')
        sqp = request.POST.getlist('selectedsqp')[0].split(',')



        additional_info = request.POST.get('additional_info')
        care_instructions = request.POST.get('care_instructions')
        thumbnail_img = request.FILES.get('thumbnail_img')

        meta_tags = request.POST.get('meta_tags')
        meta_description = request.POST.get('meta_description')
        
        product = Product.objects.create(
              name=product_name,img=thumbnail_img,
              description=product_description,
              additional_info=additional_info,
              care_instructions=care_instructions,
              brand =Brand.objects.get(id=brand_id),
            category = ProductCategory.objects.get(id=category_id),
            subcategory =ProductSubCategory.objects.get(id=subcategory_id),

            meta_tags = meta_tags,
            meta_description=meta_description
            
        )

        if detail_category_id:
              product.detail_category=ProductDetailCategory.objects.get(id=detail_category_id)


        for i in sqp:
            product.size_quantity_price.add(i)
        product.save()

     

        return redirect('products_dashboard')




     brands = Brand.objects.all()[::-1] 
     brand_id = request.GET.get('brand_id',0)
     category_id = request.GET.get('category_id',0)
     subcategory_id = request.GET.get('subcategory_id',0)



     if brand_id:
        categories = ProductCategory.objects.filter(brand__id =brand_id)[::-1]
     else:
        categories=None

     if category_id:
            subcategories = ProductSubCategory.objects.filter(category__id=category_id)[::-1]
     else:
            subcategories =None

     if subcategory_id:
            detail_categories = ProductDetailCategory.objects.filter(subcategory__id=subcategory_id)[::-1]
     else:
            detail_categories =None

     

      
     sqpies = SizeQuantityPrice.objects.all()[::-1]
     if brand_id:
        cntx ={
            'title':'Add Product',
            'brand_id':uuid.UUID(brand_id),
            'brands':brands,
            'categories':categories,
            'sqpies':sqpies,
            'charges':DeliveryCharges.objects.all()[::-1] 


        }
     
        if category_id:
                cntx={           
                  'title':'Add Product',
                  'brand_id':uuid.UUID(brand_id),
                  'brands':brands,
                  'subcategories':subcategories,
                  'category_id':uuid.UUID(category_id),
                  'categories':categories,
                  'sqpies':sqpies,

                }
        if subcategory_id:
                cntx={

                 'title':'Add Product',
                'brand_id':uuid.UUID(brand_id),
                'brands':brands,
                'subcategories':subcategories,
                'category_id':uuid.UUID(category_id),
                'categories':categories,
                'subcategory_id':uuid.UUID(subcategory_id),
                'detail_categories':detail_categories,
                'sqpies':sqpies,

                }
        
     else:
           cntx ={
            'title':'Add Product',
            'brands':brands,
            'sqpies':sqpies,

        } 
     return render(request,'back-end/add-new-product.html',cntx)


def addproduct_crud(request,id):
      slug= request.GET.get('slug')
      product = Product.objects.get(id=id)
      if slug == 'update':
            if request.method == 'POST':
                  product_name = request.POST.get('product_name')
                  product_description = request.POST.get('product_description')
                  brand_id = request.POST.get('brand_id')
                  category_id = request.POST.get('category_id')
                  subcategory_id = request.POST.get('subcategory_id')
                  detail_category_id = request.POST.get('detail_category_id')
                  sqp = request.POST.getlist('selectedsqp')[0].split(',')



                  additional_info = request.POST.get('additional_info')
                  care_instructions = request.POST.get('care_instructions')
                  thumbnail_img = request.FILES.get('thumbnail_img')
                  if not thumbnail_img:
                        thumbnail_img = product.img
                  meta_tags = request.POST.get('meta_tags')
                  meta_description = request.POST.get('meta_description')
                  

                  
                  product.name = product_name
                  product.img = thumbnail_img
                  product.description = product_description
                  product.additional_info = additional_info
                  product.care_instructions = care_instructions
                  product.brand = Brand.objects.get(id=brand_id)
                  product.category = ProductCategory.objects.get(id=category_id)
                  product.subcategory = ProductSubCategory.objects.get(id=subcategory_id) 
                  
                  if detail_category_id:
                        product.detail_category = ProductDetailCategory.objects.get(id=detail_category_id)

                  product.meta_tags = meta_tags
                  product.meta_description = meta_description


                  if sqp!=['']:
                        for i in sqp:
                              product.size_quantity_price.add(i)
            
                  product.save()

                  return redirect('products_dashboard')




            brands = Brand.objects.all()[::-1] 
            brand_id = request.GET.get('brand_id',0)


            category_id = request.GET.get('category_id',0)
            subcategory_id = request.GET.get('subcategory_id',0)
            




          



            if brand_id:
                  selected_brand = Brand.objects.get(id=brand_id)
                  categories = ProductCategory.objects.filter(brand__id =brand_id)[::-1]
          

            if category_id:
                        selected_category = ProductCategory.objects.get(id=category_id)
                        subcategories = ProductSubCategory.objects.filter(category__id=category_id)[::-1]
            

            if subcategory_id:
                        selected_subcategory = ProductSubCategory.objects.get(id=subcategory_id)
                        detail_categories = ProductDetailCategory.objects.filter(subcategory__id=subcategory_id)[::-1]
            
        


            sqpies = SizeQuantityPrice.objects.all()[::-1] 
            selected_sqpies = product.size_quantity_price.all()[::-1] 


            
            if brand_id:
                  cntx ={
                        'title':'Update Product',
                        'selected_brand':selected_brand,
                        'brands':brands,
                        'categories':categories,
                        'sqpies':sqpies,
                        'selected_sqpies':selected_sqpies,
                        'pro_id':id,
                        'product':product,

                  }
            
                  if category_id:
                        cntx={    'title':'Update Product',

                        'selected_brand':(selected_brand),
                        'brands':brands,
                        'subcategories':subcategories,
                        'selected_category':selected_category,
                        'categories':categories,
                        'sqpies':sqpies,
                       'product':product, 
                        'pro_id':id,



                        }
                  if subcategory_id:
                        cntx={

                        'title':'Update Product',

                        'selected_brand':(selected_brand),
                        'brands':brands,
                        'subcategories':subcategories,
                        'selected_category':(selected_category),
                        'categories':categories,
                        'selected_subcategory':(selected_subcategory),
                        'detail_categories':detail_categories,
                        'sqpies':sqpies,
                        'pro_id':id,   
                        'product':product, 



                        }
                  
            else:
                  cntx ={
                        'title':'Update Product',

                        'brands':brands,
                        'sqpies':sqpies,
                        'selected_sqpies':selected_sqpies,
                        'pro_id':id,
                        'product':product,



                  } 
            return render(request,'back-end/edit-product.html',cntx)





















      if slug=='delete':
            product = Product.objects.get(id =id)
            product.delete()
            return redirect('products_dashboard')
      


def sqp_list(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      sqp_list = SizeQuantityPrice.objects.all()[::-1] 
      return render(request,'back-end/sqp_list.html',{'title':'SQP','sqp_list':sqp_list})


def sqp_crud(request):
      slug = request.GET.get('slug')
      if slug == 'Update':
            id = request.GET.get('id')

            if request.method == 'POST':
                color_type = request.POST.get('color_type')
                color=request.POST.get('color')
                color_family = request.POST.get('color_family')
                name = request.POST.get('name')
                size=request.POST.get('size')
                price=request.POST.get('price')
                quantity=request.POST.get('quantity')
                discount=request.POST.get('discount')
                discount_percentage=float(request.POST.get('update_discounted_prcentage',0.0))
                img = request.FILES.get('img')

                discounted_price=float(request.POST.get('update_discounted_price',0.0))

            #     if color_type == "multi_color":
            #           color= color.split(',')
                print(color_family)

                sqp = SizeQuantityPrice.objects.get(id=id)


                if color_family not in ["None" ,None ,''] :
                  family =ColourFamily.objects.get(name = color_family)
                  sqp.color_family = family
                
                if img: 
                  sqp.img = img
                sqp.name =name
                sqp.color_type=color_type
                sqp.color = color
                sqp.size = size
                sqp.price = price
                sqp.quantity = quantity
                sqp.discount = discount
                sqp.discount_percentage = discount_percentage
                sqp.discounted_price = discounted_price
               
                sqp.save()

                messages.success(request,'Updated')

                return redirect('sqp_list')
            else:
                sqp =SizeQuantityPrice.objects.get(id=id)   
                return render(request,'back-end/add-sqp.html',{'title':'Add SQP','sqp':sqp,'slug':'Update','color_family':ColourFamily.objects.all()})
      
      
      if slug == 'Add':
        if request.method == 'POST':
                color_type = request.POST.get('color_type')

                color=request.POST.get('color')
                color_family = request.POST.get('color_family')
                img = request.FILES.get('img')

                name=request.POST.get('name')
                size=request.POST.get('size')
                price=request.POST.get('price')
                quantity=request.POST.get('quantity')
                discount=request.POST.get('discount')
                discount_percentage=float(request.POST.get('discount_percentage',0.0))

                discounted_price=float(request.POST.get('add_discounted_price',0.0))
          

            #     if color_type == "multi_color":
            #           color= color.split(',')
            #     print(color_family)
                sqp =SizeQuantityPrice.objects.create(name=name,
                      color=color,size=size,price=price,quantity=quantity,discount=discount,discount_percentage=discount_percentage,
                      discounted_price=discounted_price
                )     
                sqp.img =img
                sqp.color_type=color_type
                if color_family !="None":
                  family =ColourFamily.objects.get(name = color_family)
                  sqp.color_family=family
                else:
                      pass
                sqp.save()           

                messages.success(request,'Added')

                return redirect('sqp_list')
      
        return render(request,'back-end/add-sqp.html',{'title':'Add SQP','slug':'Add','color_family':ColourFamily.objects.all()})
      
      if slug =='Delete':
            id = request.GET.get('id') 
            sqp = SizeQuantityPrice.objects.get(id=id)
            sqp.delete()
            return redirect('sqp_list') 
      



def users_list(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      

      
      users =User.objects.all() 
      slug = request.GET.get('slug')
      if slug=='Add':
            pass
      if slug == 'update':
            pass
      if slug =='delete':
            id = request.GET.get('id')
            user = User.objects.filter(email=id)
            user.delete()
            return redirect('users_list')

      cntx={
            'users':users[::-1],
      }
      return render(request,'back-end/all-users.html',cntx)

def media_dashboard(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      products =Product.objects.all()[::-1] 
      return render(request, 'back-end/media.html',{'title':'Product Images','products':products})

def img_products(request,id):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      slug=request.GET.get('slug')
      if slug =='Add':
            if request.method == 'POST':

                  img = request.FILES.get('img')
                  product=Product.objects.get(id=id)
                  pro_img = ProductImages.objects.create(img=img, products=product,)
                  pro_img.save()
                  return redirect('img_products',id)
            

      if slug == 'delete':
            img_id = request.GET.get('img_id')
            pro_img = ProductImages.objects.get(id=img_id)
            pro_img.delete()
            return redirect('img_products',id)
      
      product_imgs = ProductImages.objects.filter(products__id=id)
      return render(request,"back-end/img-product.html",{'title':'Media','product_imgs':product_imgs,'id':id})


def coupons_list(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      slug= request.GET.get('slug')
      if slug == 'Add':
            if request.method == 'POST':
                  selected_products = request.POST.get('selected_products').split(',')
                  code=request.POST.get('code')
                  active = request.POST.get('active')
                  percentage = request.POST.get('percentage')
                  coupon = DiscountCoupon.objects.create(code=code,percentage=percentage)
                  for pro_id in selected_products:
                    product = Product.objects.get(id=pro_id)
                    coupon.products.add(product)
                  if active == 'True':
                        coupon.active = True
                  coupon.save()
                  return redirect('coupons_list')
            products=Product.objects.all()[::-1] 
            return render(request, 'back-end/add-new-coupon.html',{'products':products,'slug':'Add'})

      coupons = DiscountCoupon.objects.all()[::-1] 
      return render(request,'back-end/coupon-list.html',{'coupons':coupons})

def coupons_crud(request,id):
      slug= request.GET.get('slug')
      
            

      if slug == 'update':
            if request.method == 'POST':
                  selected_products = request.POST.get('selected_products').split(',')
                  code=request.POST.get('code')
                  active = request.POST.get('active')
                  percentage = request.POST.get('percentage')

                  print(selected_products,code,active,percentage)
                  coupon = DiscountCoupon.objects.get(id=id)

                  coupon.code=code
                  coupon.percentage = percentage
                  for pro_id in selected_products:
                    print(pro_id)
                    product = Product.objects.get(id=pro_id)
                    coupon.products.add(product)


                  if active == 'True':
                        coupon.active = True
                  coupon.save()
                  return redirect('coupons_list')


            coupon = DiscountCoupon.objects.get(id=id)
            products=Product.objects.all()[::-1] 
            return render(request, 'back-end/add-new-coupon.html',{'products':products,'slug':'update','coupon':coupon})
      
      if slug == 'delete':
            coupon = DiscountCoupon.objects.get(id=id)
            coupon.delete()
            return redirect('coupons_list')
      
    
# ----------- order list -----------------------------

def order_list(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      orders = Order.objects.filter(payment_status='Completed')[::-1] 
      return render(request,"back-end/order-list.html",{'title':'order-list','orders':orders})

def order_details(request,slug):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      order = Order.objects.get(serial_id=slug)
      return render(request,"back-end/order-detail.html",{'title':'order-list','order':order})


def order_tracking(request, slug):
    if not request.user.is_authenticated:
        return redirect('dashboard')
    
    if not request.user.is_superuser:
        messages.error(request, "Not Allowed")
        return redirect('dashboard')
    
    order = Order.objects.get(serial_id=slug)
    
    delivery_status = order.delivery_status  # Get the delivery status of the order
    if request.method == 'POST':
          tracking_id = request.POST.get('tracking_id')
          order_status = request.POST.get('order_status')
          expected_date = request.POST.get('expected_date')


          if not expected_date:
            expected_date = None
          else:
                  try:
                        # Ensure the date is in 'YYYY-MM-DD' format
                        datetime.datetime.strptime(expected_date, '%Y-%m-%d')
                  except ValueError:
                        # Handle the case of an invalid date format
                        print(expected_date)


          order.tracking_id = tracking_id
          order.delivery_status = order_status
          order.expected_date = expected_date
          order.save()
          return redirect('order_tracking',order.serial_id)
    
    return render(request, "back-end/order-tracking.html", {'title': 'order-list', 'order': order, 'delivery_status': delivery_status})

def order_crud(request,slug):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      slug = request.GET.get('slug')
      if slug == 'delete':
        order = Order.objects.get(serial_id=slug)
        order.delete()        
        return redirect('order_list')
      
def product_reviews(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      slug = request.GET.get('slug')
      if slug:
            Reviews.objects.get(id=slug).delete()
            return redirect('product_reviews')
      reviews = Reviews.objects.all()[::-1] 
      return render(request,"back-end/product-review.html",{'title':'Product Reviews',"reviews":reviews})

def taxes_dashboard(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      delivery_charges = DeliveryCharges.objects.all()[::-1] 
      slug = request.GET.get('slug')
      if slug:
            if slug == 'add':
                  if request.method == 'POST':
                        name = request.POST.get('name')
                        detail = request.POST.get('details')
                        charges = float(request.POST.get('charges'))

                        delivery_charges = DeliveryCharges.objects.create(
                              country_name=name,details=detail,charges=charges
                        )
                        delivery_charges.save()
                        return redirect('taxes_dashboard') 
                  return render(request,'back-end/add-deliveryChargers.html',{'title':'Add Charges','slug':'add'})
            
            if slug == 'update':
                  print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                  id = request.GET.get('id')
                  delivery_charges =DeliveryCharges.objects.get(id=id)
                  if request.method == 'POST':
                        name = request.POST.get('name')
                        charges = float(request.POST.get('charges'))
                        detail = request.POST.get('details')



                        delivery_charges.country_name =name
                        delivery_charges.details = detail
                        delivery_charges.charges= charges
                        delivery_charges.save()
                        return redirect('taxes_dashboard') 
                  return render(request,'back-end/add-deliveryChargers.html',{'title':'Update delivery Charges','slug':'update','delivery_charges':delivery_charges})
            if slug == 'delete':
                  id = request.GET.get('id')

                  DeliveryCharges.objects.get(id=id).delete()
                  return redirect('taxes_dashboard')

      return render(request,"back-end/deliveryChargers.html",{'title':'Delivery Chargers','delivery_charges':delivery_charges})





#-------------- Articles -------------------
def all_articles(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      slug = request.GET.get('slug')
      id = request.GET.get('id')
      if slug :
            if slug == 'Add':
                  if request.method == 'POST':
                        name= request.POST.get('name')
                        writer= request.POST.get('writer')
                        description= request.POST.get('description')
                        content= request.POST.get('content')
                        meta_tags= request.POST.get('meta_tags')
                        meta_description= request.POST.get('meta_description')
                        thumbnail_img = request.FILES.get('thumbnail_img')
                        


                        tags_list = parse_tags(meta_tags)

                        # Create or retrieve the tags
                        tags = []
                        for tag_name in tags_list:
                              tag, created = Tag.objects.get_or_create(name=tag_name)
                              tags.append(tag)

                        # Associate the tags with your model instance

                        article = Articles.objects.create(
                              name=name,writer=writer,description=description,content=content,meta_description=meta_description,
                              meta_tags=meta_tags,thumbnail = thumbnail_img
                        )
                        article.tags.set(*tags)
                        article.save()
                        return redirect('all_articles')



                  else:
                        return render(request,"back-end/add-article.html",{'title':'CRUD','slug':slug})




            if slug == 'update':
                  article = Articles.objects.get(id=id)

                  if request.method == 'POST':
                        
                        name= request.POST.get('name')
                        writer= request.POST.get('writer')
                        description= request.POST.get('description')
                        content= request.POST.get('content')
                        meta_tags= request.POST.get('meta_tags')
                        meta_description= request.POST.get('meta_description')
                        thumbnail_img = request.FILES.get('thumbnail_img')

                        tags_list = parse_tags(meta_tags)

                        # Create or retrieve the tags
                        tags = []
                        for tag_name in tags_list:
                              tag, created = Tag.objects.get_or_create(name=tag_name)
                              tags.append(tag)
                              article.tags.set(tags)

                        article.name=name
                        article.writer =writer
                        article.description =description
                        article.content =content
                        article.meta_tags =meta_tags
                        article.meta_description =meta_description
                        article.thumbnail =thumbnail_img

                        article.save()
                        return redirect('all_articles')



                  else:
                        return render(request,"back-end/add-article.html",{'title':'CRUD','slug':slug,'article':article})

            if slug == 'delete':
                  Articles.objects.get(id = id).delete()
                  return redirect('all_articles')      

      articles = Articles.objects.all()[::-1] 
      return render(request,'back-end/articles.html',{'title':'Articles','articles':articles})


def invoice(request,slug):
            order = Order.objects.get(serial_id=slug)
            if order.payment_status == 'Completed':
                  
                  return render(request,'invoice/invoice-1.html',{'title':f'#{order.serial_id}','order':order})
            else:
                  return render(request, "404.html")



def custom_order(request):
    return redirect('posr')


def pos(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      

      try:
            order_id=request.session['orderId']

            order_deatils = Order.objects.get(serial_id=order_id)
                            

      except:
            order_deatils =None



      if request.method =='POST':
                  if request.GET.get('createorder'):
                        try:
                              order_id =request.session['orderId']
                              order = Order.objects.get(serial_id=order_id)
                        except:
                              messages.error(request,'User Details Not added')
                              return redirect('pos')


                        tax_percentage = request.POST.get('tax_percentage')
                        discount_type = request.POST.get('discount_type')
                        discount = request.POST.get('discount')
                        deliveryCountry = request.POST.get('Dcountry')
                        deliveryCharges = request.POST.get('Dcountry_amount')
                        total = request.POST.get('total')
                        try:
                              dcharg = DeliveryCharges.objects.get(id=deliveryCountry)
                        except:
                              messages.error(request,"Select Shipping Country")
                              return redirect('pos')
                        selected_product_list=request.session['selected_product_list']

                        for  item in selected_product_list:
                              product_name = item['product']
                              product =Product.objects.get(name=product_name)



                              orderItem = OrderItem.objects.create(
                                    product =product,
                                    quantity= int(item['qty']),
                                    sqp_code = item['sqp']['name'],
                                    color = item['sqp']['color'],
                                    size = item['sqp']['size'],
                                    price = item['sqp']['price'],
                                    total = item['total'],
                                    discount_price = item['discount_price']
                              ) 
                              orderItem.save()
                              order.order_items.add(orderItem)
                              order.save()


                        order.sub_total = request.session['sub_total']
                        order.tax_percentage=tax_percentage


                        if discount_type == 'Percentage':
                              order.discount_percentage = discount
                        if discount_type == 'Amount':
                              order.discount_amount = discount


                        order.deliveryCountry = dcharg.country_name
                        if order.sub_total <= 100: 
                              order.deliveryCharges = float(deliveryCharges)
                        order.payment_amount = total

                        order.payment_status = 'Completed'
                        order.payment_id = "Store Transaction"

                        
                        order.save()


                        del request.session['selected_product_list']
                        del request.session['sub_total']
                        del request.session['orderId']

                        messages.success(request,"order Created")
                        return redirect('invoice',order_id)
                    
                  name = request.POST.get('customer_name')
                  email = request.POST.get('customer_email')
                  contact = request.POST.get('customer_contact')
                  address_line_1 = request.POST.get('address_line_1')
                  address_line_2 = request.POST.get('address_line_2',None)
                  city = request.POST.get('city')
                  state = request.POST.get('state')
                  country = request.POST.get('country')
                  postal_code = request.POST.get('postal_code')


                  if request.GET.get('userinfo') == 'Add':
    
                        order = Order.objects.create(
                              customer_name=name,
                              customer_email=email,
                              customer_contact=contact,
                              address_line_1=address_line_1,
                              address_line_2=address_line_2,
                              city=city,
                              state=state,
                              country=country,
                              postal_code=postal_code,
                              payment_status='Pending',
                              delivery_status='Order Processing',

                        )

                  if request.GET.get('userinfo') == 'Update':
                              order_id=request.session['orderId']

                              order = Order.objects.get(serial_id=order_id)
                              order.customer_name=name
                              order.customer_email=email
                              order.customer_contact=contact
                              order.address_line_1=address_line_1
                              order.address_line_2=address_line_2
                              order.city=city
                              order.state=state
                              order.country=country
                              order.postal_code=postal_code
                              order.payment_status='Pending'
                              order.delivery_status='Order Processing'

                  order.save()
                  request.session['orderId']=order.serial_id
                  return redirect('pos')
       
      aproduct = request.GET.get('aproduct')
      sqp_id =request.GET.get('sqp')
      qty =request.GET.get('qty')
      rm_product = request.GET.get('rm_product')
      selected_product_list= request.session.get('selected_product_list',[])
      orderitem_name = request.GET.get('orderitem_name')

      sub_total = 0
      if qty:
            for  item in  (selected_product_list):
                  if item['product'] == orderitem_name and item['sqp']['id']==sqp_id :
                        item['qty'] = qty

                        if item['discount']=='active':
                              item['total'] = round(int(qty) * float(item['sqp']['discounted_price']),2)

                        else:
                              item['total'] = round(int(qty) * float(item['sqp']['price']),2)
                        
                  sub_total = round(float(sub_total + float(item['total'])),2)



            request.session['sub_total'] = sub_total
            request.session['selected_product_list'] = selected_product_list


            return redirect('pos')

      if rm_product:
            for  item in  (selected_product_list):
                  if item['product'] == rm_product:
                        selected_product_list.remove(item)
                        break

            for  item in  (selected_product_list):    
                  sub_total = round(float(sub_total + float(item['total'])),2)
 
            request.session['sub_total'] = sub_total
            

            request.session['selected_product_list'] = selected_product_list
            return redirect('pos')




      if aproduct:
            product = Product.objects.get(id=aproduct)
            sqp = SizeQuantityPrice.objects.get(id=sqp_id)


            serializer = size_quantity_price_serializer(sqp)
            sqp =serializer.data

            if sqp['discount_percentage']:
                  discount = 'active'
                  discount_price = float(sqp['price']) - float(sqp['discounted_price'])


                  selected_product_list.append({'product': product.name,'discount':discount,'discount_price':discount_price ,'sqp': sqp,'qty':1,'total':sqp['discounted_price']})

            else:
                  discount = None
                  discount_amount = 0.00

                  selected_product_list.append({'product': product.name,'discount':None, 'discount_price':0.00, 'sqp': sqp,'qty':1,'total':sqp['price']})
            # del request.session['selected_product_list']
            request.session['selected_product_list'] = selected_product_list

            print("!!!!!!!!!!!!!!!!!!!!!!!\n",selected_product_list)
            for  item in  (selected_product_list):    
                  sub_total = round(float(sub_total + float(item['total'])),2)
 
            request.session['sub_total'] = sub_total
            return redirect('pos')

      
      products = Product.objects.all() 
      product_list=[]   
      for product in products:
            for sqp in product.size_quantity_price.all() :
                  product_list.append({'product':product,'sqp':sqp})
      
      Dcountry = request.GET.get('Dcountry')
      try:
            dcharg = DeliveryCharges.objects.get(id=Dcountry)
      except:
            dcharg = {
                  'country_name':None,
                  'charges':0
            }

      # if  Dcountry:
      #       order_deatils.deliveryCharges = 0

      #       if order_deatils.sub_total < 100:
      #             order_deatils.deliveryCharges = float(dcharg.charges)
                  

      #       order_deatils.deliveryCountry = dcharg.country_name
      #       order_deatils.payment_amount = order_deatils.sub_total +  order_deatils.deliveryCharges
      #       order_deatils.save()
      #       return redirect('pos')
      delivery_charges=DeliveryCharges.objects.all()
      
      return render(request,"back-end/pos.html",{'title':'Zeba | Billing System','product_list':product_list,'order_deatils':order_deatils,
                                          'delivery_charges':delivery_charges,'dcharg':dcharg})
      


def colour_family_dashboard(request):
      slug = request.GET.get('slug')
      id = request.GET.get('id')
      if slug == 'delete':
                  ColourFamily.objects.get(id=id).delete()
                  messages.success(request,"Deleted Successfully")
                  return redirect('colour_family_dashboard')
      if request.method == 'POST':
            

            name = request.POST.get('name')
            ColourFamily.objects.create(name=name).save()
            messages.success(request,"Added Successfully")

            return redirect('colour_family_dashboard')
      
      if slug =='add':
            return render(request,'back-end/colour-family-list.html',{'title':'Colour Family','status':'ADD'})
      return render(request,'back-end/colour-family-list.html',{'title':'Colour Family','family':ColourFamily.objects.all()})






def support_tickets(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      support_tickets=SupportTickets.objects.all()[::-1] 
      return render(request,"back-end/support-ticket.html",{'title':'Support Tickets','support_tickets':support_tickets})


def todoList_crud(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      
      if request.method == 'POST':
            name = request.POST.get('name')
            
            TodoList.objects.create(name=name).save()

      checked = request.GET.get('CHECKED')
      id = request.GET.get('id')

      if checked == 'TRUE':
            todolist = TodoList.objects.get(id=id)
            todolist.checked = True
            todolist.delete()
      
      return redirect('dashboard')

      

def revenue_data(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      

      monthly_revenue = (
      Order.objects
      .filter(payment_status='Completed')
      .annotate(month=TruncMonth('created_at'))
      .values('month')
      .annotate(revenue=Sum('payment_amount'))
      .order_by('month')
      )

      # Create a list of dictionaries for the monthly revenue as floats
      revenue_list = [
      {month['month'].strftime('%B'): float(month['revenue'])}
      for month in monthly_revenue
      ]
      return JsonResponse(revenue_list,safe=False)

def scrolling_banner_images(request):
      if request.method == 'POST':
            img = request.FILES.get('img')
            
            banner = HomeBannerScrolling.objects.create(img=img)
            banner.save()
      if request.GET.get('delete'):
            img_id = request.GET.get('img_id')
            banner = HomeBannerScrolling.objects.get(id=img_id)
            banner.delete()
      banner_imgs =  HomeBannerScrolling.objects.all()
      return render(request,'back-end/scrolling-banner.html',{'title':'Scolling Banner','banner_imgs':banner_imgs})

def banner_images(request):
      if not request.user.is_authenticated:
            return redirect('dashboard')
    
      if not request.user.is_superuser:
         messages.error(request,"Not Allowed")
         return redirect('dashboard')
      if request.method == 'POST':
                  

            img_1600X978 = request.FILES.get('best_seller_banner_1600x978')
            img_375x586 = request.FILES.get('advertisment_375x586')
            banner = HomeBannerImages.objects.first()

            if img_1600X978:
                  banner.best_seller_banner_1600x978 =img_1600X978 
            if img_375x586:
                  banner.advertisment_375x586 = img_375x586
            banner.save()
            return redirect('banner_images')
        
      banner = HomeBannerImages.objects.first()
      
      return render(request,'back-end/banners.html',{'title':'Banner images','banner':banner})



def return_orders_lst(request):
      return_orders = ReturnOrders.objects.all()[::-1]
      return render(request,'back-end/return_order_list.html',{'return_orders':return_orders})