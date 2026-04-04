import uuid
from decimal import Decimal
from django.db import models
from apps.products.models import Product


class Order(models.Model):
    """Order model with Nuvei tax breakdown for Ecuador."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        PAYMENT_SENT = 'payment_sent', 'Enlace Enviado'
        PAID = 'paid', 'Pagado'
        CANCELLED = 'cancelled', 'Cancelado'
        REFUNDED = 'refunded', 'Reembolsado'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pendiente'
        APPROVED = 'approved', 'Aprobado'
        REJECTED = 'rejected', 'Rechazado'
        CANCELLED = 'cancelled', 'Cancelado'

    class InstallmentsType(models.IntegerChoices):
        CORRIENTE = 0, 'Corriente'
        CON_INTERESES = 2, 'Con Intereses'
        SIN_INTERESES = 3, 'Sin Intereses'

    class TaxPercentage(models.IntegerChoices):
        IVA_0 = 0, '0%'
        IVA_8 = 8, '8%'
        IVA_15 = 15, '15%'

    class Environment(models.TextChoices):
        STG = 'STG', 'Staging'
        PROD = 'PROD', 'Producción'

    # Customer info
    customer_name = models.CharField('Nombre Cliente', max_length=200)
    customer_phone = models.CharField('Teléfono Cliente', max_length=20)
    customer_email = models.CharField('Email Cliente', max_length=200)

    # Order status
    status = models.CharField('Estado', max_length=20, choices=Status.choices, default=Status.PENDING)

    # Tax breakdown (Nuvei Ecuador format)
    subtotal = models.DecimalField(
        'Base Imponible (taxable_amount)', max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    vat_amount = models.DecimalField(
        'Monto IVA (vat)', max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    tax_percentage = models.IntegerField(
        'Porcentaje IVA', choices=TaxPercentage.choices, default=TaxPercentage.IVA_15
    )
    total = models.DecimalField(
        'Total a Pagar (amount)', max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    installments_type = models.IntegerField(
        'Tipo de Cuotas', choices=InstallmentsType.choices, default=InstallmentsType.CORRIENTE
    )

    # Payment info
    payment_url = models.URLField('URL de Pago', blank=True)
    payment_status = models.CharField(
        'Estado Pago', max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    nuvei_transaction_id = models.CharField('Nuvei Transaction ID', max_length=100, blank=True)
    authorization_code = models.CharField('Código de Autorización', max_length=100, blank=True)
    dev_reference = models.CharField('Dev Reference', max_length=100, unique=True, blank=True)
    ltp_id = models.CharField('Link to Pay ID', max_length=100, blank=True)
    environment = models.CharField(
        'Ambiente', max_length=4, choices=Environment.choices, default=Environment.STG
    )

    # Timestamps
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.dev_reference:
            self.dev_reference = f'ORD-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate totals from order items and apply IVA."""
        items_subtotal = sum(item.subtotal for item in self.items.all())
        self.subtotal = items_subtotal
        rate = Decimal(str(self.tax_percentage)) / Decimal('100')
        self.vat_amount = (self.subtotal * rate).quantize(Decimal('0.01'))
        self.total = self.subtotal + self.vat_amount

    def __str__(self):
        return f'Orden {self.dev_reference} - ${self.total}'


class OrderItem(models.Model):
    """Individual item within an order."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Orden')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Producto')
    quantity = models.PositiveIntegerField('Cantidad', default=1)
    unit_price = models.DecimalField('Precio Unitario', max_digits=10, decimal_places=2)
    subtotal = models.DecimalField('Subtotal', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Orden'
        verbose_name_plural = 'Items de Orden'

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.quantity}x {self.product.name} @ ${self.unit_price}'
