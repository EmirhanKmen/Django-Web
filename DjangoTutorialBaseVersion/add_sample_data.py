#!/usr/bin/env python
"""
Django Anket Sitesi - Örnek Veri Ekleme Script
Bu script veritabanına örnek anketler ve seçenekleri ekler.
"""

import os
import django
from django.utils import timezone

# Django ayarlarını yükle
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangotutorial.settings')
django.setup()

from polls.models import Question, Choice

def add_sample_data():
    """Örnek verileri veritabanına ekle"""
    
    # Mevcut verileri temizle (isteğe bağlı)
    Question.objects.all().delete()
    print("✓ Eski veriler temizlendi")
    
    # Anket 1: Programlama Dili
    q1 = Question.objects.create(
        question_text="Hangi programlama dili en iyi?",
        pub_date=timezone.now()
    )
    choices_q1 = [
        ("Python", 45),
        ("JavaScript", 38),
        ("Java", 32),
        ("C++", 18),
    ]
    for choice_text, votes in choices_q1:
        Choice.objects.create(question=q1, choice_text=choice_text, votes=votes)
    print("✓ Anket 1 eklendi: 'Hangi programlama dili en iyi?'")
    
    # Anket 2: Web Framework
    q2 = Question.objects.create(
        question_text="En iyi web framework'ü hangisi?",
        pub_date=timezone.now()
    )
    choices_q2 = [
        ("Django", 72),
        ("React", 65),
        ("Vue.js", 42),
        ("Angular", 28),
    ]
    for choice_text, votes in choices_q2:
        Choice.objects.create(question=q2, choice_text=choice_text, votes=votes)
    print("✓ Anket 2 eklendi: 'En iyi web framework'ü hangisi?'")
    
    # Anket 3: Uyku Saati
    q3 = Question.objects.create(
        question_text="Kaç saat uyku uyuyorsunuz günlük?",
        pub_date=timezone.now()
    )
    choices_q3 = [
        ("5-6 saat", 23),
        ("7-8 saat", 89),
        ("8+ saat", 34),
    ]
    for choice_text, votes in choices_q3:
        Choice.objects.create(question=q3, choice_text=choice_text, votes=votes)
    print("✓ Anket 3 eklendi: 'Kaç saat uyku uyuyorsunuz günlük?'")
    
    # Anket 4: Favori Renk
    q4 = Question.objects.create(
        question_text="Favori renginiz hangisidir?",
        pub_date=timezone.now()
    )
    choices_q4 = [
        ("Mavi", 56),
        ("Kırmızı", 42),
        ("Yeşil", 38),
        ("Sarı", 19),
        ("Mor", 25),
    ]
    for choice_text, votes in choices_q4:
        Choice.objects.create(question=q4, choice_text=choice_text, votes=votes)
    print("✓ Anket 4 eklendi: 'Favori renginiz hangisidir?'")
    
    print("\n🎉 Tüm örnek veriler başarıyla eklendi!")
    print(f"📊 Toplam {Question.objects.count()} anket, {Choice.objects.count()} seçenek kaydedildi.")

if __name__ == "__main__":
    try:
        add_sample_data()
    except Exception as e:
        print(f"❌ Hata oluştu: {e}")
