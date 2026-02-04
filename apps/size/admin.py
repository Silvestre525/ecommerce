from django.contrib import admin

from .models import Size


# Register your models here.
@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
