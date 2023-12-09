from django.urls import path
from .views import *
urlpatterns = [
    path('Brands/',Brands,name="brands"),
    path('<uuid:uuid>/',product_inside,name="product_inside"),
    path('all-products/',allproducts,name="allproducts"),
  

    path('checkout/',Checkout,name="checkout"),

    
    #API for category list
    path('cat_list/',cat_list,name="cat_list"),


    #All Product Page Filters 
    # path('price-filter/',Price_Filter,name="Price_Filter"),
    path('category-filter/<uuid:slug>/',cat_filter,name="cat_filter"),
    path('category/<str:slug>/',category,name="category"),

    path('color-filter/<str:slug>/',Color_Filter,name="color_filter"),
    path('discounted_products',Discount_filter,name="discount_products"),
    path('brand-filter/<uuid:uuid>',brand_filter,name="brand_filter"),

    path('search/',Search,name='search')
    ,path('deals-on-products',Deal_filter,name="deals-on-products"),

    path('review_post/<uuid:id>',review_post,name="review_post")

    # path('paymentgateway/',paymentGateway,name="paymentgateway"),
    # path('success_page',success_page,name='success_page')

    ]