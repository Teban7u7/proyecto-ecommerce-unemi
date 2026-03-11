from django.contrib import admin
from .models import Category, Product, Stock


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class StockInline(admin.StackedInline):
    model = Stock
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price', 'get_stock', 'is_active')
    list_filter = ('category', 'is_active', 'brand')
    search_fields = ('name', 'brand', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [StockInline]

    def get_stock(self, obj):
        try:
            return obj.stock.quantity
        except Stock.DoesNotExist:
            return 'Sin stock'
    get_stock.short_description = 'Stock'


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'min_quantity', 'is_low_stock', 'updated_at')
    list_filter = ('updated_at',)
    search_fields = ('product__name',)

    def is_low_stock(self, obj):
        return obj.is_low_stock
    is_low_stock.boolean = True
    is_low_stock.short_description = 'Stock Bajo'
