from django.contrib import admin

from .models import Color


# Register your models here.
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ("id", "title")
    search_fields = ("title",)
