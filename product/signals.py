from django.db.models.signals import post_save,post_delete
from django.dispatch import receiver
from .models import  Product, SizeQuantityPrice,DiscountOnProducts
from authentication.models import Cart




@receiver(post_save, sender=DiscountOnProducts)



def update_price_with_discount(sender, instance, **kwargs):
    """
    Update the price fields of SizeQuantityPrice objects when a new DiscountCoupon is created
    and associated with a Product object.
    """
    products = instance.products.all()
    for product in products:
        sqps = product.size_quantity_price.all()
        for sqp in sqps:
            if sqp.price:
                original_price = float(sqp.price)
                percentage = float(instance.percentage)
                discounted_price = original_price - (original_price * percentage / 100)
                sqp.discount_percentage = f'{percentage}%'
                sqp.discounted_price = discounted_price
                sqp.discount = True
                sqp.save()

        carts = Cart.objects.filter(product=product)
        for cart in carts:
            cart.total_price= int(cart.quantity) *float(cart.size_quantity_price.discounted_price)
            cart.save()



@receiver(post_delete, sender=DiscountOnProducts)
def clear_discount_fields(sender, instance, **kwargs):
    """
    Clear the discount-related fields in SizeQuantityPrice objects when a DiscountOnProducts object is deleted.
    """
    products = instance.products.all()
    for product in products:
        sqps = product.size_quantity_price.all()
        for sqp in sqps:
            sqp.discount_percentage = None
            sqp.discounted_price = None
            sqp.discount = False
            sqp.save()

        carts = Cart.objects.filter(product=product)
        for cart in carts:
            cart.total_price= int(cart.quantity) *float(cart.size_quantity_price.discounted_price)
            cart.save()