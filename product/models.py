from django.db import models
import uuid
from ckeditor.fields import RichTextField 
# Create your models here.
import os


class DeliveryCharges(models.Model):
    country_name = models.CharField(max_length=50)
    charges = models.FloatField(null=True,blank=True)
    details = models.TextField()
    def __str__(self):
        return self.country_name



def sqp_image_path(instance, filename):
    name = str(instance.name)[::-1]
    path = name[-1:-5:-1]
    return os.path.join('SQP', str(path), filename)


class ColourFamily(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
class SizeQuantityPrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name=models.CharField(max_length=100,null=True, blank=True)
    img = models.FileField(upload_to=sqp_image_path, null=True, blank=True)

    color_type = models.JSONField(default=list,null=True,blank=True)
    color = models.CharField(max_length=400, null=True, blank=True)
    size = models.CharField(max_length=400, null=True, blank=True)
    color_family = models.ForeignKey(ColourFamily,on_delete=models.CASCADE,null=True, blank=True)

    

    quantity = models.CharField(max_length=400)
    price = models.CharField(max_length=400)
    discount = models.BooleanField(default=False,null=True,blank=True)
    discount_percentage = models.FloatField(null=True, blank=True,)
    discounted_price = models.FloatField(null=True, blank=True,)



    # dimension_type_choices = (
    #     ("Inch", "Inch"),
    #     ("Millimeter", "Millimeter"),
    #     ("Centimeter", "Centimeter"),
    # )
    # dimension_type = models.CharField(max_length=400,choices=dimension_type_choices, null=True, blank=True)
    # length = models.CharField(max_length=400, null=True, blank=True)
    # width = models.CharField(max_length=400, null=True, blank=True)
    # height = models.CharField(max_length=400, null=True, blank=True)

    # weight_type_choices = (
    #     ("Gram", "Gram"),
    #     ("Kilogram", "Kilogram"),
    #     ("Pound", "Pound"),
    #     ("Ounce", "Ounce"),
    # )
    # weight_type = models.CharField(max_length=400, choices=weight_type_choices, null=True, blank=True)
    # weight = models.CharField(max_length=400, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    # sort_order = models.PositiveIntegerField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    

class Brand(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    img = models.ImageField(upload_to='brands/',null=True, blank=True)
    details = models.CharField(max_length=400,null=True, blank=True)
    address = models.CharField(max_length=400, null=True,blank=True)
    contact = models.CharField(max_length=400, null=True,blank=True)

    name = models.CharField(max_length=400)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name


    
class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=400)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name



class ProductSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=400)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name



class ProductDetailCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=400)
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
    


def product_image_path(instance, filename):
    return os.path.join('Products', str(instance.name), filename)

def image_path(instance, filename):
    return os.path.join('Products', str(instance.products.name), filename)

class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=400)
    img = models.ImageField(upload_to=product_image_path, null=True, blank=True)
    description = RichTextField(null=True, blank=True)
    additional_info = RichTextField(null=True, blank=True)
    care_instructions = RichTextField(null=True, blank=True)

    size_quantity_price = models.ManyToManyField(SizeQuantityPrice)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    detail_category = models.ForeignKey(ProductDetailCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='products')

    meta_tags = models.CharField(max_length=400, null=True, blank=True)
    meta_description = models.CharField(max_length=400, null=True, blank=True)
    is_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class ProductImages(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    products = models.ForeignKey(Product,on_delete=models.CASCADE)
    img = models.ImageField(upload_to=image_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DiscountCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=400)
    percentage = models.FloatField()
    products = models.ManyToManyField(Product,null=True,blank=True)
    active= models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class DiscountOnProducts(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    img_offer_583x157 = models.ImageField(upload_to='Home/offer_583x157',null=True,blank=True)
    products = models.ManyToManyField(Product,blank=True)
    end_date = models.DateTimeField()
    percentage = models.CharField(max_length=400)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)









