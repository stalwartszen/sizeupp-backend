from django.urls import path
from authentication import views

from django.contrib.auth.views import PasswordResetConfirmView

urlpatterns = [
    path('home', views.home,name="home"),

    
    path('auth/signup', views.signup,name="signup"),
    path('auth/signin', views.signin,name="signin"),
    path('auth/logout', views.logout_view,name="logout"),
    

    path('auth/forgot_password',views.forgot_password,name="forgot_password"),
    path('auth/otp',views.otp,name="otp"),
    path ('auth/forgot-otp',views.otp_forgot_pass,name="otp_forgot_pass"),

    # Update Details Url's
    path('userprofile',views.userprofile,name='userprofile'),
    path('address',views.address,name='address_add'),
    path('address/<uuid:id>/<str:slug>',views.address_by_id,name='address_crud'),


    # path('card',views.card,name='card_add'),
    # path('card/<uuid:id>/<str:slug>',views.card_by_id,name='card_crud'),
    
    path('track-order/',views.Track_order,name="track_order"),

    path('add-to-cart/<uuid:uuid>',views.Add_Cart,name="add_cart"),
    path('my-cart',views.show_Cart,name="show_cart"), 
    path('delete_cart/<uuid:uuid>',views.del_cart,name="del_item"),

    path('wishlist/',views.wishlist,name="wishlist"),
    path('add_wishlist/<uuid:uuid>',views.add_wishlist,name="add_wishlist"),
    path('remove_wishlist/<uuid:uuid>',views.remove_wishlist,name="remove_wishlist"),
        #   path('cart/<uuid:id>/<str:slug>',views.cart_by_id,name='cart_crud'),

    # path('create-order',views.order,name='crate_order'),
    
    #Main Pages Url's
    path('contactus',views.contactus,name="contactus"),
    
    # path('aboutus-us/',views.contactus,name="contactus"),

    path('create-order', views.create_order, name='create_order'),
    path('payment/execute', views.payment_execute, name='payment_execute'),
    path('payment/cancel', views.payment_cancel, name='payment_cancel'),

 
    #Update User Profile
    path('update-profile',views.Update_Profile,name="Update_Profile"),
    path('update-cart/<uuid:uuid>',views.updateCart,name="updateCart"),

    path('return-product',views.return_product,name='return_product')

]