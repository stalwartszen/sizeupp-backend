# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ExcelFile
import pandas as pd
from product.models import *



@receiver(post_save, sender=ExcelFile)
def handle_excel_file_upload(sender, instance, created, **kwargs):
    if created:
        # Trigger Celery task to process each row of the Excel file
        excel_file = ExcelFile.objects.get(pk=instance.id)
        df = pd.read_excel(excel_file.file.path)
        for index, row in df.iterrows():
        # Iterate through all columns in the row
            print(index)
            var = {}
            for col_name, value in row.items():
                # Print or save the values as per your requirement
                var[col_name] = value
            
            
            
            if Product.objects.all() and int(Product.objects.order_by('-id')[0].id) == int(var['Generic']):
                        product = Product.objects.order_by('-id')[0]
            else:
                        product = Product.objects.create(id = var['Generic'])
                        product.season = var['Season']
                        product.season_code = var['Season code']
                        product.color = var['COLOR']
                        product.mrp = var['MRP']
                        product.sleeve = var['SLEEVE']
                        product.design_surface = var['DESIGN/SURFACE']
                        product.occasion = var['OCCASION']
                        product.name = var['Product Title']
                        product.fit = var['FIT']
                        product.neck_type = var['NECK TYPE']
                        # product.gender = var['Gender']
                        product.fabric_detail = var['FABRIC DETAILS']
                        product.Washcare = var['Washcare']
                        
                        product.launch_date = var['Launch Date']
                        product.is_enable = var['is_enable']
                        product.model_size = var['model_size']
                        product.mc_desc = var['MC Desc.']
                        product.style = var['STYLE']
                        product.manufacturer = var['Manufacturer name']


                        if ProductCategory.objects.filter(name=var['Category']).exists():
                            category =  ProductCategory.objects.get(name=var['Category'])
                        else:
                            category =  ProductCategory.objects.create(name=var['Category'])

                        product.category = category
                        
                        if ProductSubCategory.objects.filter(category=category,name=var['Sub-Category']).exists():
                            subcategory =  ProductSubCategory.objects.get(category=category,name=var['Sub-Category'])
                        else:
                            subcategory =  ProductSubCategory.objects.create(category=category,name=var['Sub-Category'])
                            
                            
                        product.subcategory = subcategory
                        
                        
                        if ProductSubSubCategory.objects.filter(subcategory=subcategory,name=var['Sub-Sub-Category']).exists():
                            subsubcategory =  ProductSubSubCategory.objects.get(subcategory=subcategory,name=var['Sub-Category'])
                        else:
                            subsubcategory =  ProductSubSubCategory.objects.create(subcategory=subcategory,name=var['Sub-Category'])
                            
                            
                        product.subsubcategory = subsubcategory
                        
                        
                        
                        if ColourFamily.objects.filter(name=var['Color Family']).exists():
                            colour_family = ColourFamily.objects.get(name=var['Color Family'])
                        else:
                            colour_family = ColourFamily.objects.create(name=var['Color Family'])

                            product.color_family = colour_family
                        product.save()
                        
            sqp = SizeQuantityPrice.objects.create(
                            id = var['Article'],
                            ean_code = var['EAN code'],
                            size = var['SIZE'],
                            inches = var['inches'],
                            length = var['Length (cm)'],
                            width = var['Width (cm)'],
                            weight = var['Weight (gm)'],
                            quantity =var['Stock Quantity'],
                            centimeter = var['cm']
                        )
            sqp.save()
            product.sqp.add(sqp)
            product.save()
                    
                