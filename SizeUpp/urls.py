from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from dashboard.views import invoice
# Media files

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('api/product/', include('product.urls')),
    path('dashboard/', include('dashboard.urls')),
    path("", include("django.contrib.auth.urls")), 
    path('invoice/<slug:slug>',invoice,name='invoice'),

     # new

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

