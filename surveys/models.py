"""
Sahaflar Platformu — Surveys Models
Advanced survey engine with multiple question types, categories,
conditional logic, geolocation, and expiration support.
"""
import uuid

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone

from core.models import TimeStampedModel


class Category(TimeStampedModel):
    """Survey categories for organization and filtering."""
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name="Açıklama")
    icon = models.CharField(max_length=50, default='GEN', verbose_name="Ikon")
    color = models.CharField(max_length=7, default='#00F0A0', verbose_name="Renk Kodu")

    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['name']

    def __str__(self):
        return self.name


class Survey(TimeStampedModel):
    """
    Main survey model — the evolution of the simple Question model.
    Supports multiple question types, categories, expiration, and access control.
    """

    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Taslak'
        ACTIVE = 'ACTIVE', 'Aktif'
        PAUSED = 'PAUSED', 'Duraklatıldı'
        CLOSED = 'CLOSED', 'Kapatıldı'
        ARCHIVED = 'ARCHIVED', 'Arşivlendi'

    class Priority(models.TextChoices):
        LOW = 'LOW', 'Düşük'
        MEDIUM = 'MEDIUM', 'Orta'
        HIGH = 'HIGH', 'Yüksek'
        CRITICAL = 'CRITICAL', 'Kritik'

    # Identity
    title = models.CharField(max_length=300, verbose_name="Anket Başlığı")
    slug = models.SlugField(unique=True, max_length=350)
    description = models.TextField(blank=True, verbose_name="Açıklama")
    access_code = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name="Erişim Kodu")

    # Relations
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_surveys',
        verbose_name="Oluşturan"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='surveys',
        verbose_name="Kategori"
    )

    # Status & Scheduling
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Durum"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name="Öncelik"
    )
    pub_date = models.DateTimeField(verbose_name="Yayın Tarihi", default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Bitiş Tarihi")

    # Settings
    is_public = models.BooleanField(default=True, verbose_name="Herkese Açık")
    allow_anonymous = models.BooleanField(default=False, verbose_name="Anonim Yanıta İzin Ver")
    require_location = models.BooleanField(default=False, verbose_name="Konum Zorunlu")
    max_responses = models.PositiveIntegerField(null=True, blank=True, verbose_name="Maks. Yanıt Sayısı")

    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Enlem")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name="Boylam")
    location_name = models.CharField(max_length=200, blank=True, verbose_name="Konum Adı")

    class Meta:
        verbose_name = "Anket"
        verbose_name_plural = "Anketler"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('surveys:detail', kwargs={'slug': self.slug})

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE and not self.is_expired

    @property
    def response_count(self):
        return self.responses.count()

    @property
    def question_count(self):
        return self.questions.count()

    def can_respond(self, user=None):
        """Check if a user can respond to this survey."""
        if not self.is_active:
            return False
        if self.max_responses and self.response_count >= self.max_responses:
            return False
        if not self.allow_anonymous and (user is None or not user.is_authenticated):
            return False
        return True


class Question(TimeStampedModel):
    """
    Survey question supporting multiple types.
    Evolved from the simple polls Question model.
    """

    class QuestionType(models.TextChoices):
        SINGLE_CHOICE = 'SINGLE', 'Tek Seçimli'
        MULTIPLE_CHOICE = 'MULTIPLE', 'Çoklu Seçimli'
        TEXT = 'TEXT', 'Açık Uçlu Metin'
        NUMBER = 'NUMBER', 'Sayısal'
        RATING = 'RATING', 'Derecelendirme (1-5)'
        YES_NO = 'YESNO', 'Evet / Hayır'
        DATE = 'DATE', 'Tarih'
        SLIDER = 'SLIDER', 'Kaydırma (0-100)'

    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name="Anket"
    )
    text = models.TextField(verbose_name="Soru Metni")
    question_type = models.CharField(
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_CHOICE,
        verbose_name="Soru Tipi"
    )
    is_required = models.BooleanField(default=True, verbose_name="Zorunlu")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")
    help_text = models.CharField(max_length=500, blank=True, verbose_name="Yardım Metni")

    # For slider type
    min_value = models.IntegerField(default=0, verbose_name="Min Değer")
    max_value = models.IntegerField(default=100, verbose_name="Max Değer")

    class Meta:
        verbose_name = "Soru"
        verbose_name_plural = "Sorular"
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.survey.title} — {self.text[:50]}"

    @property
    def response_count(self):
        return self.answers.count()


class Choice(TimeStampedModel):
    """Answer choices for single/multiple choice questions."""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name="Soru"
    )
    text = models.CharField(max_length=300, verbose_name="Seçenek Metni")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıra")

    class Meta:
        verbose_name = "Seçenek"
        verbose_name_plural = "Seçenekler"
        ordering = ['order']

    def __str__(self):
        return self.text

    @property
    def vote_count(self):
        return self.selected_answers.count()

    @property
    def percentage(self):
        total = self.question.response_count
        if total == 0:
            return 0
        return round((self.vote_count / total) * 100, 1)


class Response(TimeStampedModel):
    """
    A single survey submission by a respondent.
    Groups all answers for one survey completion.
    """
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name="Anket"
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='survey_responses',
        verbose_name="Yanıtlayan"
    )
    session_id = models.UUIDField(default=uuid.uuid4, verbose_name="Oturum ID")

    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Adresi")
    user_agent = models.TextField(blank=True, verbose_name="Tarayıcı Bilgisi")
    completion_time = models.DurationField(null=True, blank=True, verbose_name="Tamamlanma Süresi")
    is_complete = models.BooleanField(default=False, verbose_name="Tamamlandı")

    class Meta:
        verbose_name = "Yanıt"
        verbose_name_plural = "Yanıtlar"
        ordering = ['-created_at']

    def __str__(self):
        user = self.respondent or "Anonim"
        return f"{self.survey.title} — {user}"


class Answer(TimeStampedModel):
    """Individual answer to a single question within a response."""
    response = models.ForeignKey(
        Response,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Yanıt"
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name="Soru"
    )

    # Answer data — flexible storage
    text_answer = models.TextField(blank=True, verbose_name="Metin Yanıtı")
    number_answer = models.DecimalField(
        max_digits=10, decimal_places=2,
        null=True, blank=True,
        verbose_name="Sayısal Yanıt"
    )
    selected_choices = models.ManyToManyField(
        Choice,
        blank=True,
        related_name='selected_answers',
        verbose_name="Seçilen Seçenekler"
    )
    date_answer = models.DateField(null=True, blank=True, verbose_name="Tarih Yanıtı")

    class Meta:
        verbose_name = "Cevap"
        verbose_name_plural = "Cevaplar"
        unique_together = ['response', 'question']

    def __str__(self):
        return f"Cevap: {self.question.text[:30]}"
