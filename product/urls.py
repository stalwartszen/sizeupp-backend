from django.urls import path
from .views import *
urlpatterns = [
    path('<uuid:uuid>/',product_inside,name="product_inside"),
    path('all-products',allproducts,name="allproducts"),
  


    
    #API for category list
    path('category-details',cat_list,name="cat_list"),



    path('review_post',review_post,name="review_post"),
    path('filter',productfilter,name="productfilter"),
    
  
    ]