from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Category for liquor products (e.g. Whisky, Ron, Vodka, Vino)."""
    name = models.CharField('Nombre', max_length=100, unique=True)
    slug = models.SlugField('Slug', max_length=120, unique=True, blank=True)
    description = models.TextField('Descripción', blank=True)
    image = models.ImageField('Imagen', upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField('Activa', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """Liquor product."""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Categoría',
    )
    name = models.CharField('Nombre', max_length=200)
    slug = models.SlugField('Slug', max_length=220, unique=True, blank=True)
    description = models.TextField('Descripción', blank=True)
    price = models.DecimalField('Precio (USD)', max_digits=10, decimal_places=2)
    image = models.ImageField('Imagen', upload_to='products/', blank=True, null=True)
    alcohol_content = models.DecimalField(
        'Contenido Alcohólico (%)',
        max_digits=5, decimal_places=2,
        blank=True, null=True,
    )
    volume_ml = models.PositiveIntegerField('Volumen (ml)', blank=True, null=True)
    brand = models.CharField('Marca', max_length=100, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField('Creado', auto_now_add=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f'{self.brand}-{self.name}')
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.brand} {self.name}' if self.brand else self.name


class Stock(models.Model):
    """Stock tracking for each product."""
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='stock',
        verbose_name='Producto',
    )
    quantity = models.PositiveIntegerField('Cantidad', default=0)
    min_quantity = models.PositiveIntegerField('Cantidad Mínima', default=5)
    last_restocked = models.DateTimeField('Último Reabastecimiento', blank=True, null=True)
    updated_at = models.DateTimeField('Actualizado', auto_now=True)

    class Meta:
        verbose_name = 'Stock'
        verbose_name_plural = 'Stock'

    @property
    def is_low_stock(self):
        return self.quantity <= self.min_quantity

    @property
    def is_available(self):
        return self.quantity > 0

    def __str__(self):
        return f'{self.product.name}: {self.quantity} unidades'
