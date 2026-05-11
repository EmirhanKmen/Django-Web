"""
Sahaflar Platformu — URL Configuration
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, redirect
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.db.models import Count

from surveys.models import Survey, Response, Category
from django.contrib.auth import get_user_model


def landing_page(request):
    """Public landing page — the first impression."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    User = get_user_model()
    stats = {
        'surveys': Survey.objects.count(),
        'responses': Response.objects.filter(is_complete=True).count(),
        'users': User.objects.count(),
        'categories': Category.objects.count(),
    }
    features = [
        {'title': 'Kitap Talep Anketleri', 'desc': 'Okur taleplerini toplamak icin esnek anket akislari'},
        {'title': 'Konum Bazli Listeleme', 'desc': 'Sahaf lokasyonlarina gore filtreleme ve raporlama'},
        {'title': 'Gercek Zamanli Analitik', 'desc': 'Anlik grafikler ile talep trendlerini izleyin'},
        {'title': 'Rol Bazli Erisim', 'desc': 'Sahaf, editor ve yonetici seviyelerinde yetkilendirme'},
        {'title': 'Responsive Tasarim', 'desc': 'Mobil, tablet ve masaustu uyumlu arayuz'},
        {'title': 'REST API', 'desc': 'Sahaf sistemleriyle entegrasyon icin API katmani'},
    ]
    return render(request, 'landing.html', {'stats': stats, 'features': features})


def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)

def custom_500(request):
    return render(request, 'errors/500.html', status=500)


urlpatterns = [
    path('', landing_page, name='home'),
    path('accounts/', include('accounts.urls')),
    path('surveys/', include('surveys.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('contact/', include([
        path('', __import__('notifications.views', fromlist=['contact_view']).contact_view, name='contact'),
    ])),
    path('api/v1/', include('api.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    try:
        import debug_toolbar
        urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    except ImportError:
        pass

handler404 = 'mysite.urls.custom_404'
handler500 = 'mysite.urls.custom_500'

admin.site.site_header = 'Sahaflar Platformu Yonetimi'
admin.site.site_title = 'Sahaflar Admin'
admin.site.index_title = 'Platform Yonetim Paneli'
