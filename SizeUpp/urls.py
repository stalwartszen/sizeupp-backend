from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import invoice
# Media files
# from django.urls import re_path
# from rest_framework import permissions
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi

from rest_framework.authtoken import views

# schema_view = get_schema_view(
#     openapi.Info(
#         title="SizeUpp API",
#         default_version='v1',
#         description="SizeUpp API description",
#         terms_of_service="https://www.yourapp.com/terms/",
#         contact=openapi.Contact(email="contact.hrithikhadawale@gmail.com"),
#         license=openapi.License(name="Your License"),
#     ),
#     public=True,
# )

# urlpatterns = [
    
# ]


    
urlpatterns = [
    path('admin/', admin.site.urls),
    # re_path(r'^api/token/', views.obtain_auth_token, name='obtain-token'),

    path('api/', include('authentication.urls')),
    path('api/product/', include('product.urls')),
    path('', include('dashboard.urls')),
    # path("", include("django.contrib.auth.urls")), 
    path('invoice/<slug:slug>',invoice,name='invoice'),


     # new

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns = [
#         re_path(r'^__debug__/', include(debug_toolbar.urls)),
#     ] + urlpatterns
    