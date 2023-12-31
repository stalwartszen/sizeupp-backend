# myapp/management/commands/map_images_to_products.py

import os
from django.core.management.base import BaseCommand
from product.models import Product, ProductImages

class Command(BaseCommand):
    help = 'Map images to corresponding Products'

    def handle(self, *args, **options):
        root_directory = 'media/products'

        for gender_folder in sorted(os.listdir(root_directory)):
            # print(gender_folder)
            gender_path = os.path.join(root_directory, gender_folder)
            # print(gender_path)
            if os.path.isdir(gender_path):
                not_found=[]
                for product_folder in sorted(os.listdir(gender_path)):
                    # print(product_folder)
                    product_id = product_folder.split('_')[0]
                    
                    # print(product_id)
                    try:
                        product = Product.objects.get(id=product_id)

                        product_image_folder = os.path.join(gender_path, product_folder)
                        for image_file in sorted(os.listdir(product_image_folder)):
                            # print("!@@@@######", image_file)
                            image_path = os.path.join(product_image_folder, image_file)
                            ProductImages.objects.create(products=product, img=image_path).save()

                    except Exception as e:
                        not_found.append([product_id,os.path.join(gender_path, product_folder)])
                        
                print(not_found)