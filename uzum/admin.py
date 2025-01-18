from django.contrib import admin
from django.db import models
from django_summernote.widgets import SummernoteWidget
from uzum.models import Category, ProductImage, Product



# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'description')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}



class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Yangi mahsulot uchun 1 bo'sh maydon ko'rsatiladi

class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('name_uz', 'price', 'created_at')
    search_fields = ('name_uz',)
    formfield_overrides = {
        models.TextField: {'widget': SummernoteWidget},
    }

admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)