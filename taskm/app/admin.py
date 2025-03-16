from django.contrib import admin

from .models import Employee, Product, SalesPlan, Sale

admin.site.register(Employee)
admin.site.register(Product)
admin.site.register(SalesPlan)
admin.site.register(Sale)
