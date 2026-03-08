from django.contrib import admin
from .models import StoreConfig


@admin.register(StoreConfig)
class StoreConfigAdmin(admin.ModelAdmin):
    """Store configuration admin with grouped fieldsets."""
    list_display = ('store_name', 'environment', 'iva_percentage', 'updated_at')

    fieldsets = (
        ('Tienda', {
            'fields': ('store_name',),
        }),
        ('🔄 Switch de Ambiente', {
            'fields': ('environment',),
            'description': 'Cambia entre Staging (pruebas) y Producción con un solo click.',
        }),
        ('🔑 Credenciales Nuvei — Staging', {
            'fields': (
                'nuvei_app_code_client_stg', 'nuvei_app_key_client_stg',
                'nuvei_app_code_server_stg', 'nuvei_app_key_server_stg',
            ),
            'classes': ('collapse',),
        }),
        ('🔑 Credenciales Nuvei — Producción', {
            'fields': (
                'nuvei_app_code_client_prod', 'nuvei_app_key_client_prod',
                'nuvei_app_code_server_prod', 'nuvei_app_key_server_prod',
            ),
            'classes': ('collapse',),
        }),
        ('🎨 Checkout Theme (conf)', {
            'fields': ('checkout_logo_url', 'checkout_primary_color'),
            'description': 'Personalización visual del modal de pago Nuvei.',
        }),
        ('💰 Configuración Fiscal', {
            'fields': ('iva_percentage', 'default_installments_type'),
        }),
        ('📱 WhatsApp', {
            'fields': ('whatsapp_number',),
        }),
        ('🔗 URLs de Callback', {
            'fields': ('webhook_url', 'success_url', 'failure_url', 'pending_url'),
            'classes': ('collapse',),
        }),
    )

    def has_add_permission(self, request):
        # Singleton: only allow one instance
        return not StoreConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
