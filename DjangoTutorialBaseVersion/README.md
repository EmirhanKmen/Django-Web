# Django Anket Sitesi

Basit bir anket uygulaması. Django kullanılarak geliştirilmiştir.

## Kurulum

```bash
# Django kur
pip install django

# Sunucuyu başlat
python manage.py runserver
```

Tarayıcıda aç: `http://127.0.0.1:8000/`

## Kullanım

- Anketleri görüntüle ve oy ver
- Admin paneli: `http://127.0.0.1:8000/admin/`

## Proje Yapısı

```
polls/
├── models.py       # Veri modelleri
├── views.py        # Sayfa kodları
├── urls.py         # URL rotalama
├── admin.py        # Admin ayarları
└── templates/      # HTML dosyaları
```

## Teknolojiler

- Python
- Django
- Bootstrap
- Chart.js
