from django.db import models
from django.core.cache import cache


class StoreConfig(models.Model):
    """
    Singleton model for store configuration.
    Controls the STG/PROD environment switch and Nuvei checkout theming.
    """

    class Environment(models.TextChoices):
        STG = 'STG', 'Staging (Desarrollo)'
        PROD = 'PROD', 'Producción'

    class IvaPercentage(models.IntegerChoices):
        IVA_0 = 0, '0%'
        IVA_8 = 8, '8%'
        IVA_15 = 15, '15%'

    class InstallmentsType(models.IntegerChoices):
        CORRIENTE = 0, 'Corriente'
        CON_INTERESES = 2, 'Con Intereses'
        SIN_INTERESES = 3, 'Sin Intereses'

    # Store info
    store_name = models.CharField('Nombre de la Tienda', max_length=200, default='Licorería')

    # === ENVIRONMENT SWITCH ===
    environment = models.CharField(
        'Ambiente Activo',
        max_length=4,
        choices=Environment.choices,
        default=Environment.STG,
        help_text='Cambia entre Staging (pruebas) y Producción (real).',
    )

    # === NUVEI CREDENTIALS - STAGING ===
    nuvei_app_code_client_stg = models.CharField(
        'App Code Client (STG)', max_length=100, default='TEBANSTG-EC-CLIENT'
    )
    nuvei_app_key_client_stg = models.CharField(
        'App Key Client (STG)', max_length=200, blank=True
    )
    nuvei_app_code_server_stg = models.CharField(
        'App Code Server (STG)', max_length=100, default='TEBANSTG-EC-SERVER'
    )
    nuvei_app_key_server_stg = models.CharField(
        'App Key Server (STG)', max_length=200, blank=True
    )

    # === NUVEI CREDENTIALS - PRODUCTION ===
    nuvei_app_code_client_prod = models.CharField(
        'App Code Client (PROD)', max_length=100, blank=True
    )
    nuvei_app_key_client_prod = models.CharField(
        'App Key Client (PROD)', max_length=200, blank=True
    )
    nuvei_app_code_server_prod = models.CharField(
        'App Code Server (PROD)', max_length=100, blank=True
    )
    nuvei_app_key_server_prod = models.CharField(
        'App Key Server (PROD)', max_length=200, blank=True
    )

    # === CHECKOUT THEME (conf object) ===
    checkout_logo_url = models.URLField(
        'Logo Checkout URL',
        default='https://cdn.paymentez.com/img/nv/nuvei_logo.png',
        help_text='URL del logo que aparece en el modal de Nuvei Checkout.',
    )
    checkout_primary_color = models.CharField(
        'Color Primario Checkout',
        max_length=7,
        default='#C800A1',
        help_text='Color hexadecimal (ej: #C800A1) para el tema del Checkout.',
    )

    # === FISCAL ===
    iva_percentage = models.IntegerField(
        'Porcentaje IVA',
        choices=IvaPercentage.choices,
        default=IvaPercentage.IVA_15,
        help_text='Tarifa de IVA a aplicar (0%, 8% o 15%).',
    )
    default_installments_type = models.IntegerField(
        'Tipo de Cuotas por Defecto',
        choices=InstallmentsType.choices,
        default=InstallmentsType.CORRIENTE,
    )

    # === WHATSAPP ===
    whatsapp_number = models.CharField(
        'Número WhatsApp', max_length=20, default='593XXXXXXXXX',
        help_text='Número con código de país (ej: 593999888777).',
    )

    # === CALLBACK URLS ===
    webhook_url = models.URLField('Webhook URL', blank=True)
    success_url = models.URLField('URL Pago Exitoso', blank=True)
    failure_url = models.URLField('URL Pago Fallido', blank=True)
    pending_url = models.URLField('URL Pago Pendiente', blank=True)

    # === META ===
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Tienda'
        verbose_name_plural = 'Configuración de Tienda'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton pattern
        cache.delete('store_config')
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Prevent deletion

    @classmethod
    def get_config(cls):
        """Get the singleton config instance, using cache."""
        config = cache.get('store_config')
        if config is None:
            config, _ = cls.objects.get_or_create(pk=1)
            cache.set('store_config', config, timeout=300)
        return config

    def get_active_credentials(self):
        """Return the active Nuvei credentials based on current environment."""
        if self.environment == self.Environment.PROD:
            return {
                'app_code_client': self.nuvei_app_code_client_prod,
                'app_key_client': self.nuvei_app_key_client_prod,
                'app_code_server': self.nuvei_app_code_server_prod,
                'app_key_server': self.nuvei_app_key_server_prod,
                'ccapi_url': 'https://ccapi.paymentez.com',
                'noccapi_url': 'https://noccapi.paymentez.com',
            }
        return {
            'app_code_client': self.nuvei_app_code_client_stg,
            'app_key_client': self.nuvei_app_key_client_stg,
            'app_code_server': self.nuvei_app_code_server_stg,
            'app_key_server': self.nuvei_app_key_server_stg,
            'ccapi_url': 'https://ccapi-stg.paymentez.com',
            'noccapi_url': 'https://noccapi-stg.paymentez.com',
        }

    def get_checkout_conf(self):
        """Return the conf object for Nuvei Checkout init_reference (v3)."""
        return {
            'style_version': '2',
            'theme': {
                'logo': self.checkout_logo_url,
                'primary_color': self.checkout_primary_color,
            }
        }

    def __str__(self):
        return f'{self.store_name} — {self.get_environment_display()}'
