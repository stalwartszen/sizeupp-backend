from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import  Cart

@receiver(post_save, sender=Cart)
def update_price_with_discount(sender, instance, **kwargs):
    # Disconnect the signal
    post_save.disconnect(update_price_with_discount, sender=Cart)

    price = instance.size_quantity_price.price
    if instance.size_quantity_price.discounted_price:
        price = instance.size_quantity_price.discounted_price

    instance.total_price = float(price) * int(instance.quantity)
    instance.save()

    # Reconnect the signal
    post_save.connect(update_price_with_discount, sender=Cart)


