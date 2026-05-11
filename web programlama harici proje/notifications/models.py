"""Sahaflar Platformu — Notification Models"""
from django.conf import settings
from django.db import models
from core.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Type(models.TextChoices):
        SURVEY_RESPONSE = 'RESPONSE', 'Yeni Yanıt'
        SURVEY_EXPIRING = 'EXPIRING', 'Süre Dolmak Üzere'
        SYSTEM = 'SYSTEM', 'Sistem'
        INFO = 'INFO', 'Bilgi'

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INFO)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Bildirim"
        verbose_name_plural = "Bildirimler"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"

    def mark_read(self):
        self.is_read = True
        self.save(update_fields=['is_read', 'updated_at'])


class ActivityLog(TimeStampedModel):
    """Audit trail — tracks every critical action on the platform."""
    class Action(models.TextChoices):
        LOGIN = 'LOGIN', 'Giriş Yaptı'
        LOGOUT = 'LOGOUT', 'Çıkış Yaptı'
        SURVEY_CREATED = 'SURVEY_CREATE', 'Anket Oluşturdu'
        SURVEY_UPDATED = 'SURVEY_UPDATE', 'Anket Güncelledi'
        SURVEY_DELETED = 'SURVEY_DELETE', 'Anket Sildi'
        RESPONSE_SUBMITTED = 'RESPONSE', 'Yanıt Gönderdi'
        PROFILE_UPDATED = 'PROFILE', 'Profil Güncelledi'
        EXPORT = 'EXPORT', 'Rapor Dışa Aktardı'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=Action.choices)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = "Aktivite Kaydı"
        verbose_name_plural = "Aktivite Kayıtları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.get_action_display()}"


class ContactMessage(TimeStampedModel):
    """Contact/feedback form submissions."""
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    subject = models.CharField(max_length=200, verbose_name="Konu")
    message = models.TextField(verbose_name="Mesaj")
    is_resolved = models.BooleanField(default=False, verbose_name="Çözüldü")

    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"
