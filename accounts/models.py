"""
Sahaflar Platformu — Accounts Models
Custom User model with role-based access control.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Provides role-based access control for the platform.

    Roles:
    - ADMIN: Full platform access, can manage all resources
    - COORDINATOR: Can create/manage surveys, view analytics
    - FIELD_AGENT: Can distribute surveys, collect responses in the field
    - CITIZEN: Can respond to public surveys
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Platform Yöneticisi'
        COORDINATOR = 'COORDINATOR', 'Koordinatör'
        FIELD_AGENT = 'FIELD_AGENT', 'Saha Görevlisi'
        CITIZEN = 'CITIZEN', 'Vatandaş'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CITIZEN,
        verbose_name="Rol"
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefon Numarası"
    )
    organization = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Kurum/Kuruluş"
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name="Profil Fotoğrafı"
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        verbose_name="Hakkında"
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Konum"
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="Doğrulanmış"
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Son Aktivite"
    )

    class Meta:
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_coordinator(self):
        return self.role in [self.Role.ADMIN, self.Role.COORDINATOR]

    @property
    def is_field_agent(self):
        return self.role in [self.Role.ADMIN, self.Role.COORDINATOR, self.Role.FIELD_AGENT]

    def get_initials(self):
        """Return user initials for avatar placeholder."""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        return self.username[:2].upper()
