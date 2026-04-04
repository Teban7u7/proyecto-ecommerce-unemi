from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('subtotal',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'dev_reference', 'customer_name', 'total', 'tax_percentage',
        'status', 'payment_status', 'environment', 'created_at',
    )
    list_filter = ('status', 'payment_status', 'environment', 'tax_percentage')
    search_fields = ('dev_reference', 'customer_name', 'customer_email', 'nuvei_transaction_id')
    readonly_fields = ('dev_reference', 'subtotal', 'vat_amount', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Cliente', {
            'fields': ('customer_name', 'customer_phone', 'customer_email'),
        }),
        ('Desglose Fiscal (Nuvei)', {
            'fields': ('subtotal', 'vat_amount', 'tax_percentage', 'total', 'installments_type'),
        }),
        ('Estado', {
            'fields': ('status', 'payment_status', 'environment'),
        }),
        ('Nuvei', {
            'fields': ('payment_url', 'nuvei_transaction_id', 'dev_reference', 'ltp_id'),
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
