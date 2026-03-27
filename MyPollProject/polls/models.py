import datetime 
from django.contrib import admin
from django.db import models
from django.utils import timezone


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('Teknoloji', 'Teknoloji'),
        ('Spor', 'Spor'),
        ('Eğitim', 'Eğitim'),
        ('Siyaset', 'Siyaset'),
        ('Sanat', 'Sanat'),
        ('Diğer', 'Diğer'),
    ]
    
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField("date published")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Diğer')
    
    def __str__(self):
        return self.question_text
    
    @admin.display(
        boolean=True,
        ordering="pub_date",
        description="Published recently?",
    )
    def was_published_recently(self):
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date <= now


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
