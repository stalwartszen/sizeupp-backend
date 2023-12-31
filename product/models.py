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
    
    

    
class ProductCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=400)    
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


class ProductSubSubCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=400)
    category = models.ForeignKey(ProductCategory,on_delete=models.CASCADE,null=True, blank=True)
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name



class SizeQuantityPrice(models.Model):
    id = models.CharField(max_length=25,primary_key=True,  editable=False)
    ean_code = models.CharField(max_length=15,editable=False)
    
    
    size = models.CharField(max_length=400, null=True, blank=True)
    
    inches = models.CharField(max_length=400, null=True, blank=True)
    centimeter = models.CharField(max_length=400, null=True, blank=True)
   
    length = models.CharField(max_length=400, null=True, blank=True)
    width = models.CharField(max_length=400, null=True, blank=True)
    weight = models.CharField(max_length=400, null=True, blank=True)
    height = models.CharField(max_length=400, null=True, blank=True)
    
    quantity = models.CharField(max_length=400)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)
    




def product_image_path(instance, filename):
    return os.path.join('Products', str(instance.name), filename)

def image_path(instance, filename):
    return os.path.join('Products', str(instance.products.name), filename)




class Product(models.Model):
    id = models.CharField(max_length=15,primary_key=True,  editable=False)
    name = models.CharField(max_length=40)
    season = models.CharField(max_length=40)
    season_code = models.CharField(max_length=40)
    

    sleeve = models.CharField(max_length =100,null=True, blank=True)
    design_surface = models.CharField(max_length =100,null=True, blank=True)
    fit = models.CharField(max_length =100,null=True, blank=True)
    neck_type = models.CharField(max_length =100,null=True, blank=True)

    occasion = models.CharField(max_length =100,null=True, blank=True)
    fabric_detail = models.TextField(null=True, blank=True)
    Washcare = models.TextField(null=True, blank=True)
    
    sqp =  models.ManyToManyField(SizeQuantityPrice)
    cf =  models.CharField(max_length=400, null=True, blank=True)
    color_family = models.ForeignKey(ColourFamily,on_delete=models.CASCADE,null=True, blank=True)
    color = models.CharField(max_length=400, null=True, blank=True)
    
    mrp = models.FloatField(max_length=400,null=True,blank=True)

    subsubcategory = models.ForeignKey(ProductSubSubCategory,on_delete=models.CASCADE,null=True,blank=True)
    
    discount = models.BooleanField(default=False,null=True,blank=True)
    discount_percentage = models.FloatField(null=True, blank=True,)
    discounted_price = models.FloatField(null=True, blank=True,)
    
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    subcategory = models.ForeignKey(ProductSubCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='products')

    launch_date= models.DateField(blank=True, null=True)
    is_enable= models.BooleanField(default = True)
    model_size= models.CharField(max_length=100,blank=True, null=True)
    mc_desc= models.CharField(max_length=100,blank=True, null=True)
    style= models.CharField(max_length=100,blank=True, null=True)
    manufacturer = models.CharField(max_length=100,blank=True, null=True)
    
    
    
    meta_tags = models.CharField(max_length=400, null=True, blank=True)
    meta_description = models.CharField(max_length=400, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # def __str__(self):
    #     return self.id
    

class ProductImages(models.Model):
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    # img = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_upload_path(instance, filename):
        gender_folder = 'Men' if instance.products.gender == 'Men' else 'Women'
        product_folder = f"{instance.products.id}_{instance.products.color.upper()}"
        return f'media/product/{gender_folder}/{product_folder}/{filename}'

    img = models.ImageField(upload_to=image_upload_path)





class DiscountCoupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=400)
    percentage = models.FloatField(null=True,blank=True)
    price = models.FloatField(null=True,blank=True)
    
    active= models.BooleanField(default=False)
    end_date = models.DateTimeField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class DiscountEvents(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # img_offer_583x157 = models.ImageField(upload_to='Home/offer_583x157',null=True,blank=True)
    name = models.CharField(max_length=400)
    subsubcategory = models.ManyToManyField(ProductSubSubCategory,blank=True)
    end_date = models.DateField()
    percentage = models.FloatField(null=True, blank=True,)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class ExcelFile(models.Model):
    file = models.FileField(upload_to='uploads/excel/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name





