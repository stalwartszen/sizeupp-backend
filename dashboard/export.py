import openpyxl
from django.http import HttpResponse
from django.core.files.base import ContentFile
from io import BytesIO

def export_products_to_excel(request, products):
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    headers = [
        'Product Name', 'Brand', 'Category', 'Subcategory', 'Detail Category',
        'Size', 'Quantity', 'Price', 'Color', 'Discount', 'Discount Percentage',
        'Discounted Price', 'Dimension Type', 'Length', 'Width', 'Height',
        'Weight Type', 'Weight', 'Is Enabled', 'Sort Order'
    ]
    sheet.append(headers)

    for product in products:
        for size_quantity_price in product.size_quantity_price.all():
            row = [
                product.name,
                product.brand.name,
                product.category.name if product.category else '',
                product.subcategory.name if product.subcategory else '',
                product.detail_category.name if product.detail_category else '',
                size_quantity_price.size,
                size_quantity_price.quantity,
                size_quantity_price.price,
                size_quantity_price.color,
                size_quantity_price.discount,
                size_quantity_price.discount_percentage,
                size_quantity_price.discounted_price,
                size_quantity_price.dimension_type,
                size_quantity_price.length,
                size_quantity_price.width,
                size_quantity_price.height,
                size_quantity_price.weight_type,
                size_quantity_price.weight,
                size_quantity_price.is_enabled,
                size_quantity_price.sort_order,
            ]
            sheet.append(row)

    # Save the workbook to a BytesIO buffer
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    # Create the HttpResponse object with the appropriate headers for file download
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=products.xlsx'

    return response
