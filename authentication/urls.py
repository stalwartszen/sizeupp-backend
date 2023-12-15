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
    path('userprofile',views.userprofile,name='userprofile'),

    # Update Details Url's
    path('address',views.address,name='address_add'),
    path('address/<uuid:id>/<str:slug>',views.address_by_id,name='address_crud'),


    # path('card',views.card,name='card_add'),
    # path('card/<uuid:id>/<str:slug>',views.card_by_id,name='card_crud'),
    
    path('track-order/',views.Track_order,name="track_order"),

    path('add-to-cart/<uuid:uuid>/<uuid:sqp_id>/',views.Add_Cart,name="add_cart"),
    path('my-cart/',views.show_Cart,name="show_cart"), 
    path('delete_cart/<uuid:uuid>',views.del_cart,name="del_item"),

    path('wishlist/',views.wishlist,name="wishlist"),
    path('add-wishlist/<uuid:uuid>',views.add_wishlist,name="add_wishlist"),
    path('remove-wishlist/<uuid:uuid>',views.remove_wishlist,name="remove_wishlist"),
        #   path('cart/<uuid:id>/<str:slug>',views.cart_by_id,name='cart_crud'),

    # path('order',views.order,name='crate_order'),
    
    #Main Pages Url's
    path('help-desk/',views.contactus,name="contactus"),
    path('about-us/',views.aboutus,name="aboutus"),
    path('faq/',views.faq,name="faq"),
    path("terms-&-conditions",views.terms_condition,name="terms_condition"),
    # path('aboutus-us/',views.contactus,name="contactus"),

    path('payment/', views.payment, name='paymentgateway'),
    path('payment/execute/', views.payment_execute, name='payment_execute'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),

    path('Articles/',views.articles,name="articles"),
    path('Article-Details/<int:id>',views.article_details,name="article_details"),

    #Update User Profile
    path('Update-Profile/',views.Update_Profile,name="Update_Profile"),
    path('updateCart/',views.updateCart,name="updateCart"),

    path('return-product',views.return_product,name='return_product')

]