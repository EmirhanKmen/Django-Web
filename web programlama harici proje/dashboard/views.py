"""
Sahaflar Platformu — Dashboard Views (Extended)
Command center, analytics, map view, reports, settings, and survey builder.
"""
from datetime import timedelta
import csv
import io
import json

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify

from surveys.models import Survey, Question, Choice, Response, Answer, Category

User = get_user_model()


@login_required
def dashboard_index(request):
    """Main dashboard — the command center."""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)

    total_surveys = Survey.objects.count()
    active_surveys = Survey.objects.filter(status=Survey.Status.ACTIVE).count()
    total_responses = Response.objects.filter(is_complete=True).count()
    responses_this_week = Response.objects.filter(is_complete=True, created_at__gte=seven_days_ago).count()
    total_users = User.objects.count()
    active_users = User.objects.filter(last_activity__gte=thirty_days_ago).count()

    recent_surveys = Survey.objects.select_related('creator', 'category').annotate(
        total_responses=Count('responses')
    ).order_by('-created_at')[:5]

    recent_responses = Response.objects.select_related('survey', 'respondent').filter(
        is_complete=True
    ).order_by('-created_at')[:10]

    categories = Category.objects.annotate(survey_count=Count('surveys')).filter(survey_count__gt=0)

    daily_responses = []
    for i in range(6, -1, -1):
        day = now - timedelta(days=i)
        count = Response.objects.filter(is_complete=True, created_at__date=day.date()).count()
        daily_responses.append({'date': day.strftime('%d/%m'), 'count': count})

    # Unread notifications count
    unread_notifs = 0
    try:
        unread_notifs = request.user.notifications.filter(is_read=False).count()
    except Exception:
        pass

    context = {
        'total_surveys': total_surveys, 'active_surveys': active_surveys,
        'total_responses': total_responses, 'responses_this_week': responses_this_week,
        'total_users': total_users, 'active_users': active_users,
        'recent_surveys': recent_surveys, 'recent_responses': recent_responses,
        'categories': categories, 'daily_responses': daily_responses,
        'unread_notifs': unread_notifs,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
def analytics_view(request):
    """Detailed analytics page."""
    now = timezone.now()
    thirty_days = now - timedelta(days=30)

    # Response trend (30 days)
    daily_trend = []
    for i in range(29, -1, -1):
        day = now - timedelta(days=i)
        count = Response.objects.filter(is_complete=True, created_at__date=day.date()).count()
        daily_trend.append({'date': day.strftime('%d/%m'), 'count': count})

    # Category stats
    cat_stats = Category.objects.annotate(
        survey_count=Count('surveys'),
        response_count=Count('surveys__responses'),
    ).values('name', 'icon', 'color', 'survey_count', 'response_count')

    # Priority distribution
    priority_stats = Survey.objects.values('priority').annotate(count=Count('id'))

    # Status distribution
    status_stats = Survey.objects.values('status').annotate(count=Count('id'))

    # Top surveys by responses
    top_surveys = Survey.objects.annotate(
        total_responses=Count('responses')
    ).order_by('-total_responses')[:10]

    # Hourly distribution (approximate with created_at hour)
    hourly = [0] * 24
    for r in Response.objects.filter(is_complete=True, created_at__gte=thirty_days):
        hourly[r.created_at.hour] += 1

    # User role distribution
    role_stats = User.objects.values('role').annotate(count=Count('id'))

    context = {
        'daily_trend': daily_trend, 'cat_stats': list(cat_stats),
        'priority_stats': list(priority_stats), 'status_stats': list(status_stats),
        'top_surveys': top_surveys, 'hourly': hourly, 'role_stats': list(role_stats),
        'total_surveys': Survey.objects.count(),
        'total_responses': Response.objects.filter(is_complete=True).count(),
        'total_users': User.objects.count(),
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required
def map_view(request):
    """Map view showing survey locations."""
    surveys = Survey.objects.filter(
        latitude__isnull=False, longitude__isnull=False
    ).annotate(total_responses=Count('responses')).values(
        'title', 'slug', 'latitude', 'longitude', 'location_name',
        'priority', 'status', 'total_responses'
    )
    
    surveys_list = list(surveys)
    for s in surveys_list:
        if s.get('latitude') is not None:
            s['latitude'] = float(s['latitude'])
        if s.get('longitude') is not None:
            s['longitude'] = float(s['longitude'])
            
    surveys_json = json.dumps(surveys_list)
    
    return render(request, 'dashboard/map.html', {'surveys_data': surveys_json})


@login_required
def export_csv(request, slug):
    """Export survey results as CSV with Injection Protection."""
    survey = get_object_or_404(Survey, slug=slug)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sahaf_{slug}_results.csv"'
    response.write('\ufeff')  # BOM for Excel UTF-8

    def clean_csv_value(value):
        """Mitigate CSV Injection by prefixing unsafe characters with a single quote."""
        val = str(value)
        if val and val[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{val}"
        return val

    writer = csv.writer(response)
    questions = survey.questions.all()
    header = ['Yanıt #', 'Tarih', 'Kullanıcı'] + [q.text[:50] for q in questions]
    writer.writerow(header)

    for idx, resp in enumerate(survey.responses.filter(is_complete=True).select_related('respondent'), 1):
        row = [idx, resp.created_at.strftime('%d/%m/%Y %H:%M'), clean_csv_value(resp.respondent or 'Anonim')]
        for q in questions:
            try:
                ans = resp.answers.get(question=q)
                if q.question_type in ['SINGLE', 'MULTIPLE', 'YESNO']:
                    row.append(clean_csv_value(', '.join(c.text for c in ans.selected_choices.all())))
                elif q.question_type in ['NUMBER', 'RATING', 'SLIDER']:
                    row.append(clean_csv_value(ans.number_answer or ''))
                else:
                    row.append(clean_csv_value(ans.text_answer))
            except Answer.DoesNotExist:
                row.append('')
        writer.writerow(row)

    return response


@login_required
def export_all_csv(request):
    """Export all surveys summary as CSV with Injection Protection."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sahaf_all_surveys.csv"'
    response.write('\ufeff')

    def clean_csv_value(value):
        """Mitigate CSV Injection by prefixing unsafe characters with a single quote."""
        val = str(value)
        if val and val[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{val}"
        return val

    writer = csv.writer(response)
    writer.writerow(['Başlık', 'Kategori', 'Durum', 'Öncelik', 'Oluşturan', 'Yanıt Sayısı', 'Soru Sayısı', 'Tarih', 'Konum'])

    for s in Survey.objects.select_related('creator', 'category').annotate(
        total_responses=Count('responses'), total_questions=Count('questions')
    ):
        writer.writerow([
            clean_csv_value(s.title), clean_csv_value(s.category or '-'), 
            clean_csv_value(s.get_status_display()), clean_csv_value(s.get_priority_display()),
            clean_csv_value(s.creator), s.total_responses, s.total_questions,
            s.created_at.strftime('%d/%m/%Y'), clean_csv_value(s.location_name or '-')
        ])

    return response


@login_required
def survey_builder(request):
    """Frontend survey builder."""
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        category_id = request.POST.get('category')
        priority = request.POST.get('priority', 'MEDIUM')
        is_public = request.POST.get('is_public') == 'on'
        allow_anonymous = request.POST.get('allow_anonymous') == 'on'
        
        location_name = request.POST.get('location_name', '').strip()
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not title:
            messages.error(request, 'Anket başlığı zorunludur.')
            return render(request, 'dashboard/builder.html', {'categories': categories})

        slug = slugify(title)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Survey.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        survey = Survey.objects.create(
            title=title, slug=slug, description=description,
            creator=request.user, priority=priority,
            is_public=is_public, allow_anonymous=allow_anonymous,
            status=Survey.Status.DRAFT,
            category_id=category_id if category_id else None,
            location_name=location_name,
            latitude=latitude if latitude else None,
            longitude=longitude if longitude else None,
        )

        # Process questions
        q_index = 0
        while True:
            q_text = request.POST.get(f'question_{q_index}_text')
            if q_text is None:
                break
            if not q_text.strip():
                q_index += 1
                continue

            q_type = request.POST.get(f'question_{q_index}_type', 'SINGLE')
            q_required = request.POST.get(f'question_{q_index}_required') == 'on'

            question = Question.objects.create(
                survey=survey, text=q_text.strip(),
                question_type=q_type, is_required=q_required, order=q_index
            )

            # Process choices for choice-based questions
            if q_type in ['SINGLE', 'MULTIPLE', 'YESNO']:
                c_index = 0
                while True:
                    c_text = request.POST.get(f'question_{q_index}_choice_{c_index}')
                    if c_text is None:
                        break
                    if c_text.strip():
                        Choice.objects.create(question=question, text=c_text.strip(), order=c_index)
                    c_index += 1

            q_index += 1

        messages.success(request, f'Anket "{title}" başarıyla oluşturuldu! Yayına almak için durumunu "Aktif" yapın.')
        return redirect('surveys:detail', slug=survey.slug)

    return render(request, 'dashboard/builder.html', {'categories': categories})


@login_required
def settings_view(request):
    """User settings page."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_preferences':
            messages.success(request, 'Tercihleriniz güncellendi.')
        return redirect('dashboard:settings')
    return render(request, 'dashboard/settings.html')
