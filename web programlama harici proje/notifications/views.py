"""Sahaflar Platformu — Notifications Views"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from .models import Notification, ActivityLog, ContactMessage
from .forms import ContactForm


@login_required
def notification_list(request):
    notifs = request.user.notifications.all()[:50]
    unread = request.user.notifications.filter(is_read=False).count()
    return render(request, 'notifications/list.html', {'notifications': notifs, 'unread_count': unread})


@login_required
@require_POST
def mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notif.mark_read()
    return JsonResponse({'status': 'ok'})


@login_required
@require_POST
def mark_all_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    messages.success(request, 'Tüm bildirimler okundu olarak işaretlendi.')
    return redirect('notifications:list')


@login_required
def notification_count_json(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})


@login_required
def activity_log_view(request):
    if not request.user.is_admin:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('dashboard:index')
    logs = ActivityLog.objects.select_related('user').all()[:100]
    return render(request, 'notifications/activity_log.html', {'logs': logs})


def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede dönüş yapacağız.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'notifications/contact.html', {'form': form})
