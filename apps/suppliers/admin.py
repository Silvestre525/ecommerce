from django.contrib import admin

from .models import Suppliers


# Register your models here.
@admin.register(Suppliers)
class SuppliersAdmin(admin.ModelAdmin):
    list_display = ("company_name", "contact_person", "contact_email", "city")
    search_fields = ("company_name",)
