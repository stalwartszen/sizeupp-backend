from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from product.models import Product, SizeQuantityPrice
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime  # Import the datetime module
import secrets

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=20)
    newsletter = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True)
    
    def __str__(self):
        return str(self.username)


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    address_line_1 = models.CharField(max_length=400)
    address_line_2 = models.CharField(max_length=400, null=True, blank=True)
    city = models.CharField(max_length=400)
    postal_code = models.CharField(max_length=400)
    country = models.CharField(max_length=400)
    state = models.CharField(max_length=400)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



card_weight_type_choices = (
        ("Visa", "Visa"),
        ("MasterCard", "MasterCard"),
    )

class Newsletter(models.Model):
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)




class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    size_quantity_price = models.ForeignKey(SizeQuantityPrice,on_delete=models.CASCADE,null=True, blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(0)])
    
    mrp = models.CharField(max_length=10,null=True,blank=True)
    
    # discount_on_price = models.CharField(max_length=10,null=True,blank=True)
    sub_total = models.CharField(max_length=10,null=True,blank=True)
    # total_price =models.CharField(max_length=400,null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)
    


    class Meta:
        unique_together = ('user', 'product')



class WishList(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user= models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now = True)
    updated_date = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'product')
    

class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sqp_code = models.CharField(max_length=400, null=True, blank=True)
    color = models.CharField(max_length=400, null=True, blank=True)

    size = models.CharField(max_length=400,null=True,blank=True)
    mrp = models.CharField(max_length=400,null=True,blank=True)
    sub_total = models.FloatField(default=0)
    # discount_price = models.FloatField(null=True,blank=True,default=0)
    # discount_percentage = models.FloatField(null=True, blank=True,)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)



class Order(models.Model):
    id = models.PositiveIntegerField(primary_key=True, default=secrets.randbelow(90000) + 10000, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)
    customer_name = models.CharField(max_length=400,null=True, blank=True)
    customer_email = models.EmailField(null=True, blank=True)
    customer_contact = models.CharField(max_length=15,null=True, blank=True)
    address_line_1 = models.CharField(max_length=400)
    address_line_2 = models.CharField(max_length=400, null=True, blank=True)
    city = models.CharField(max_length=400)
    postal_code = models.CharField(max_length=400)
    country = models.CharField(max_length=400)
    state = models.CharField(max_length=400)

    
    order_items = models.ManyToManyField(OrderItem)
    payment_status_choices = (
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    )
    payment_type= models.CharField(max_length=20,null=True,blank=True)
    payment_status = models.CharField(max_length=20, choices=payment_status_choices, default='Pending')
    payment_id = models.CharField(max_length=50, null=True, blank=True)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now_add=True)  

    delivery_status_choices = (
        ('Order Processing', 'Order Processing'),
        ('Pre-Production', 'Pre-Production'),
        ('In Production', 'In Production'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancel','Cancel')
        
    )
    coupon = models.CharField(max_length=15,null=True,blank=True)

    mrp_price = models.FloatField(default=0)
    sub_total = models.FloatField(default=0)
    deliveryCharges = models.IntegerField(validators=[MinValueValidator(0)],null=True, blank=True)
    cupon_discount = models.DecimalField(max_digits=1000000,decimal_places=2,null=True, blank=True)  
    
    # discount_on_ = models.FloatField(default=0)
    
    discount_percentage = models.DecimalField(max_digits=1000000,decimal_places=2,null=True, blank=True)  
    
    delivery_status = models.CharField(max_length=20, choices=delivery_status_choices, default='Order Processing')
    airwaybilno =models.CharField(max_length=100,null=True,blank=True)
    courier =models.CharField(max_length=100,null=True,blank=True)
    dispatch_label_url =models.CharField(max_length=100,null=True,blank=True)
    
    expected_date = models.DateField(blank=True,null=True)
    order_cancel = models.BooleanField(default=False)
    
    
    shipping_details = models.TextField(blank=True, null=True)
    def __str__(self):
        return str(self.payment_status) + '  '+str(self.id) + '  ' + str(self.payment_amount)
    
    def save(self, *args, **kwargs):
        # Override the save method to ensure a new order ID is generated each time
        if not self.id:
            self.id = secrets.randbelow(90000) + 10000
        super().save(*args, **kwargs)
