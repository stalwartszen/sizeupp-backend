from django.contrib import admin
from .models import *

class ProductCategoryInline(admin.TabularInline):
    model = ProductCategory


class ProductSubCategoryInline(admin.TabularInline):
    model = ProductSubCategory


class ProductDetailCategoryInline(admin.TabularInline):
    model = ProductDetailCategory


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductCategoryInline, ProductSubCategoryInline, ProductDetailCategoryInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "brand":
            kwargs["queryset"] = Brand.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(SizeQuantityPrice)
admin.site.register(ProductCategory)
admin.site.register(ProductDetailCategory)
admin.site.register(ProductSubCategory)
admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(DiscountCoupon)
admin.site.register(DiscountOnProducts)
admin.site.register(ProductImages)
admin.site.register(DeliveryCharges)