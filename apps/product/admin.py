from django.contrib import admin

from .models import Product


# Register your models here.
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "stock", "is_active", "color", "size")
    list_filter = ("is_active", "categories", "suppliers")
    search_fields = ("name",)
