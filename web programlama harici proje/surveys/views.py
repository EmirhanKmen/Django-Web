"""
Sahaflar Platformu — Surveys Views
Handles survey listing, detail, responding, and results.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Survey, Question, Choice, Response, Answer, Category


def survey_list(request):
    """List all active public surveys with filtering."""
    surveys = Survey.objects.filter(
        status=Survey.Status.ACTIVE,
        is_public=True,
        pub_date__lte=timezone.now(),
    ).select_related('creator', 'category').annotate(
        total_responses=Count('responses'),
        total_questions=Count('questions'),
    )

    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        surveys = surveys.filter(category__slug=category_slug)

    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        surveys = surveys.filter(priority=priority)

    # Search
    search_query = request.GET.get('q')
    if search_query:
        surveys = surveys.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    categories = Category.objects.all()

    context = {
        'surveys': surveys,
        'categories': categories,
        'current_category': category_slug,
        'current_priority': priority,
        'search_query': search_query or '',
    }
    return render(request, 'surveys/survey_list.html', context)


def survey_detail(request, slug):
    """Display survey detail and respond form."""
    survey = get_object_or_404(
        Survey.objects.select_related('creator', 'category'),
        slug=slug,
    )
    questions = survey.questions.prefetch_related('choices').all()

    # Check if user already responded
    already_responded = False
    if request.user.is_authenticated:
        already_responded = Response.objects.filter(
            survey=survey,
            respondent=request.user,
            is_complete=True,
        ).exists()

    can_respond = survey.can_respond(request.user) and not already_responded

    context = {
        'survey': survey,
        'questions': questions,
        'can_respond': can_respond,
        'already_responded': already_responded,
    }
    return render(request, 'surveys/survey_detail.html', context)


@require_POST
def survey_submit(request, slug):
    """Handle survey form submission."""
    survey = get_object_or_404(Survey, slug=slug)

    if not survey.can_respond(request.user if request.user.is_authenticated else None):
        messages.error(request, 'Bu ankete yanıt veremezsiniz.')
        return redirect('surveys:detail', slug=slug)

    # Create response
    response_obj = Response.objects.create(
        survey=survey,
        respondent=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        is_complete=True,
    )

    # Process geolocation if provided
    lat = request.POST.get('latitude')
    lng = request.POST.get('longitude')
    if lat and lng:
        try:
            response_obj.latitude = float(lat)
            response_obj.longitude = float(lng)
            response_obj.save(update_fields=['latitude', 'longitude'])
        except (ValueError, TypeError):
            pass

    # Process answers
    questions = survey.questions.prefetch_related('choices').all()
    for question in questions:
        field_name = f'question_{question.id}'
        answer_value = request.POST.get(field_name)
        answer_values = request.POST.getlist(field_name)

        if not answer_value and not answer_values:
            if question.is_required:
                messages.error(request, f'Zorunlu soru yanıtlanmadı: {question.text[:50]}')
                response_obj.delete()
                return redirect('surveys:detail', slug=slug)
            continue

        answer = Answer.objects.create(
            response=response_obj,
            question=question,
        )

        if question.question_type in [Question.QuestionType.SINGLE_CHOICE, Question.QuestionType.YES_NO]:
            try:
                choice = Choice.objects.get(id=answer_value, question=question)
                answer.selected_choices.add(choice)
            except (Choice.DoesNotExist, ValueError):
                pass

        elif question.question_type == Question.QuestionType.MULTIPLE_CHOICE:
            for val in answer_values:
                try:
                    choice = Choice.objects.get(id=val, question=question)
                    answer.selected_choices.add(choice)
                except (Choice.DoesNotExist, ValueError):
                    pass

        elif question.question_type in [Question.QuestionType.TEXT]:
            answer.text_answer = answer_value or ''
            answer.save(update_fields=['text_answer'])

        elif question.question_type in [Question.QuestionType.NUMBER, Question.QuestionType.RATING, Question.QuestionType.SLIDER]:
            try:
                answer.number_answer = float(answer_value)
                answer.save(update_fields=['number_answer'])
            except (ValueError, TypeError):
                pass

        elif question.question_type == Question.QuestionType.DATE:
            answer.text_answer = answer_value or ''
            answer.save(update_fields=['text_answer'])

    messages.success(request, 'Yanıtınız başarıyla kaydedildi! Teşekkürler.')
    return redirect('surveys:results', slug=slug)


def survey_results(request, slug):
    """Display survey results with statistics."""
    survey = get_object_or_404(
        Survey.objects.select_related('creator', 'category'),
        slug=slug,
    )
    questions = survey.questions.prefetch_related('choices', 'answers').all()

    # Build results data
    results_data = []
    for question in questions:
        q_data = {
            'question': question,
            'total_answers': question.answers.count(),
            'choices_data': [],
        }

        if question.question_type in [
            Question.QuestionType.SINGLE_CHOICE,
            Question.QuestionType.MULTIPLE_CHOICE,
            Question.QuestionType.YES_NO,
        ]:
            for choice in question.choices.all():
                count = choice.selected_answers.count()
                total = q_data['total_answers'] or 1
                q_data['choices_data'].append({
                    'choice': choice,
                    'count': count,
                    'percentage': round((count / total) * 100, 1) if total > 0 else 0,
                })

        elif question.question_type in [Question.QuestionType.RATING, Question.QuestionType.SLIDER, Question.QuestionType.NUMBER]:
            answers = question.answers.exclude(number_answer__isnull=True)
            if answers.exists():
                from django.db.models import Avg, Max, Min
                stats = answers.aggregate(
                    avg=Avg('number_answer'),
                    max_val=Max('number_answer'),
                    min_val=Min('number_answer'),
                )
                q_data['stats'] = {
                    'average': round(float(stats['avg']), 1) if stats['avg'] else 0,
                    'max': float(stats['max_val']) if stats['max_val'] else 0,
                    'min': float(stats['min_val']) if stats['min_val'] else 0,
                }

        elif question.question_type == Question.QuestionType.TEXT:
            q_data['text_answers'] = question.answers.exclude(
                text_answer=''
            ).values_list('text_answer', flat=True)[:20]

        results_data.append(q_data)

    context = {
        'survey': survey,
        'results_data': results_data,
        'total_responses': survey.responses.filter(is_complete=True).count(),
    }
    return render(request, 'surveys/survey_results.html', context)


def survey_results_json(request, slug):
    """API endpoint for real-time results (used by charts)."""
    survey = get_object_or_404(Survey, slug=slug)
    questions = survey.questions.prefetch_related('choices').all()

    data = {'questions': []}
    for question in questions:
        q_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'choices': [],
        }
        for choice in question.choices.all():
            q_data['choices'].append({
                'id': choice.id,
                'text': choice.text,
                'count': choice.selected_answers.count(),
            })
        data['questions'].append(q_data)

    data['total_responses'] = survey.responses.filter(is_complete=True).count()
    return JsonResponse(data)


@login_required
def my_surveys(request):
    """List all surveys created by the current user."""
    surveys = Survey.objects.filter(
        creator=request.user
    ).select_related('category').annotate(
        total_responses=Count('responses', filter=Q(responses__is_complete=True)),
        total_questions=Count('questions'),
    ).order_by('-created_at')

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        surveys = surveys.filter(status=status_filter)

    context = {
        'surveys': surveys,
        'current_status': status_filter or '',
        'status_choices': Survey.Status.choices,
    }
    return render(request, 'surveys/my_surveys.html', context)


@login_required
def survey_edit(request, slug):
    """Edit survey details — only owner can edit."""
    survey = get_object_or_404(Survey, slug=slug, creator=request.user)
    questions = survey.questions.prefetch_related('choices').all()
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
            return render(request, 'surveys/survey_edit.html', {
                'survey': survey, 'questions': questions, 'categories': categories,
            })

        survey.title = title
        survey.description = description
        survey.priority = priority
        survey.is_public = is_public
        survey.allow_anonymous = allow_anonymous
        survey.location_name = location_name
        survey.latitude = latitude if latitude else None
        survey.longitude = longitude if longitude else None
        survey.category_id = category_id if category_id else None
        survey.save()

        # Update existing questions
        for question in questions:
            q_text = request.POST.get(f'existing_q_{question.id}_text')
            q_type = request.POST.get(f'existing_q_{question.id}_type')
            q_required = request.POST.get(f'existing_q_{question.id}_required') == 'on'
            if q_text and q_text.strip():
                question.text = q_text.strip()
                if q_type:
                    question.question_type = q_type
                question.is_required = q_required
                question.save()

        messages.success(request, f'Anket "{title}" başarıyla güncellendi!')
        return redirect('surveys:detail', slug=survey.slug)

    context = {
        'survey': survey,
        'questions': questions,
        'categories': categories,
    }
    return render(request, 'surveys/survey_edit.html', context)


@login_required
@require_POST
def survey_delete(request, slug):
    """Delete a survey — only owner can delete."""
    survey = get_object_or_404(Survey, slug=slug, creator=request.user)
    title = survey.title
    survey.delete()
    messages.success(request, f'"{title}" anketi başarıyla silindi.')
    return redirect('surveys:my_surveys')


@login_required
@require_POST
def survey_toggle_status(request, slug):
    """Toggle survey status — only owner can change status."""
    survey = get_object_or_404(Survey, slug=slug, creator=request.user)
    new_status = request.POST.get('status')

    valid_statuses = [s[0] for s in Survey.Status.choices]
    if new_status in valid_statuses:
        old_status = survey.get_status_display()
        survey.status = new_status
        survey.save(update_fields=['status'])
        messages.success(request, f'Anket durumu "{old_status}" yerine "{survey.get_status_display()}" olarak değiştirildi.')
    else:
        messages.error(request, 'Geçersiz durum.')

    return redirect('surveys:detail', slug=survey.slug)


@login_required
@require_POST
def survey_add_question(request, slug):
    """Add a new question to an existing survey — only owner."""
    survey = get_object_or_404(Survey, slug=slug, creator=request.user)

    q_text = request.POST.get('question_text', '').strip()
    q_type = request.POST.get('question_type', 'SINGLE')
    q_required = request.POST.get('question_required') == 'on'

    if not q_text:
        messages.error(request, 'Soru metni zorunludur.')
        return redirect('surveys:edit', slug=slug)

    # Get next order number
    last_order = survey.questions.order_by('-order').values_list('order', flat=True).first() or 0

    question = Question.objects.create(
        survey=survey,
        text=q_text,
        question_type=q_type,
        is_required=q_required,
        order=last_order + 1,
    )

    # Process choices for choice-based questions
    if q_type in ['SINGLE', 'MULTIPLE', 'YESNO']:
        c_index = 0
        while True:
            c_text = request.POST.get(f'new_choice_{c_index}')
            if c_text is None:
                break
            if c_text.strip():
                Choice.objects.create(question=question, text=c_text.strip(), order=c_index)
            c_index += 1

    messages.success(request, f'Soru başarıyla eklendi: "{q_text[:50]}"')
    return redirect('surveys:edit', slug=slug)


@login_required
@require_POST
def survey_delete_question(request, slug, question_id):
    """Delete a question from a survey — only owner."""
    survey = get_object_or_404(Survey, slug=slug, creator=request.user)
    question = get_object_or_404(Question, id=question_id, survey=survey)
    q_text = question.text[:50]
    question.delete()
    messages.success(request, f'Soru silindi: "{q_text}"')
    return redirect('surveys:edit', slug=slug)
