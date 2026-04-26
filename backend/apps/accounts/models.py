from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Custom user model for the liquor store admin/staff."""

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        STAFF = 'staff', 'Personal'

    phone = models.CharField('Teléfono', max_length=20, blank=True)
    role = models.CharField(
        'Rol',
        max_length=10,
        choices=Role.choices,
        default=Role.ADMIN,
    )

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
