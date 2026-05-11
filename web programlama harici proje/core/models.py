"""
Sahaflar Platformu — Core Models
Base abstract models providing common fields for all platform models.
"""
import uuid

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    All platform models should inherit from this.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Oluşturulma Tarihi"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Güncellenme Tarihi"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UUIDModel(TimeStampedModel):
    """
    Abstract model using UUID as primary key for enhanced security.
    Prevents sequential ID enumeration attacks.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    class Meta:
        abstract = True


class SoftDeleteModel(TimeStampedModel):
    """
    Abstract model providing soft-delete functionality.
    Records are never truly deleted — they are marked as inactive.
    Useful for audit trails and recovery.
    """
    is_active = models.BooleanField(
        default=True,
        verbose_name="Aktif"
    )
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Silinme Tarihi"
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Mark record as deleted without removing from database."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])

    def restore(self):
        """Restore a soft-deleted record."""
        self.is_active = True
        self.deleted_at = None
        self.save(update_fields=['is_active', 'deleted_at', 'updated_at'])
