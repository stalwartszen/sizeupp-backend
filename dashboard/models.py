from django.db import models
import uuid
from product.models import Product
from authentication.models import *
from ckeditor.fields import RichTextField 
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager

# Create your models here.

class HomeBannerImages(models.Model):
    best_seller_banner_1600x978 = models.ImageField(upload_to="Home/Best_Seller_banner_1600x978")
    advertisment_375x586 = models.ImageField(upload_to='Home/Advertisment_375x586')

class HomeTopAd(models.Model):
    ad = models.CharField(max_length=255)
    
    
class HomeBannerScrolling(models.Model):
    img = models.ImageField(upload_to='Home/scrolling-banner-1155x670/')



    






class Reviews(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    comment = models.TextField()
    rating = models.CharField(max_length=3,null=True,blank=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at =models.DateTimeField(auto_now=True)
    

class Articles(models.Model):
    name = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to="Article-Thumbnail/")
    writer = models.CharField(max_length=20,null=True,blank=True)
    description = models.TextField()
    content = RichTextField(null=True, blank=True)
    created_at =models.DateField(auto_now_add=True)
    meta_tags = models.TextField()
    meta_description = models.TextField()
    tags = TaggableManager()


class SupportTickets(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email=models.EmailField() 
    number = models.CharField(max_length=15)
    issue= models.CharField(max_length=100,null=True,blank=True)
    message = models.TextField()
    product =models.CharField(max_length=200,null=True,blank=True)
    created=models.DateTimeField(auto_now_add=True)
    resolved =models.BooleanField(default=False)



class TodoList(models.Model):
    name = models.CharField(max_length=100)
    checked = models.BooleanField(default=False)

    def __str__(self):
        return self.name    

class ReturnOrders(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    issue = models.CharField(max_length=100)
    feedback =models.TextField(null=True,blank=True)
    created = models.DateTimeField(auto_now_add=True)

class GiftVaoucher(models.Model):
    theme = models.CharField(max_length=50)
    img = models.ImageField(upload_to='git-vaoucher/')
    
class UserGiftVoucher(models.Model):
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_contact = models.CharField(max_length=15)

    Recipient_name = models.CharField(max_length=100)
    Recipient_email = models.EmailField()
    Recipient_contact = models.CharField(max_length=15)
    theme = models.CharField(max_length=50)
    
    
    





    

