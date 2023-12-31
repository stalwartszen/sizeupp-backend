from django.contrib import admin
from .models import *

class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory


class ProductSubCategoryInline(admin.TabularInline):
    model = ProductSubCategory


admin.site.register(SizeQuantityPrice)
admin.site.register(ProductCategory)
admin.site.register(ProductSubSubCategory)
admin.site.register(ProductSubCategory)
admin.site.register(Product)
admin.site.register(ColourFamily)
admin.site.register(ExcelFile)
admin.site.register(DiscountCoupon)
admin.site.register(DiscountEvents)
admin.site.register(ProductImages)
admin.site.register(DeliveryCharges)
# admin.site.register(DiscountEvents)