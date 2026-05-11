"""
Sahaflar Platformu — Surveys Admin
Comprehensive admin interface for survey management.
"""
from django.contrib import admin

from .models import Category, Survey, Question, Choice, Response, Answer


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['text', 'order']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'is_required', 'order', 'help_text']
    show_change_link = True


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'category', 'status', 'priority',
                    'response_count', 'question_count', 'pub_date', 'expires_at']
    list_filter = ['status', 'priority', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'creator__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['access_code', 'response_count', 'question_count']
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'

    fieldsets = [
        ('Temel Bilgiler', {
            'fields': ['title', 'slug', 'description', 'category', 'creator']
        }),
        ('Durum & Zamanlama', {
            'fields': ['status', 'priority', 'pub_date', 'expires_at']
        }),
        ('Erişim Ayarları', {
            'fields': ['is_public', 'allow_anonymous', 'require_location',
                       'max_responses', 'access_code'],
            'classes': ['collapse'],
        }),
        ('Konum', {
            'fields': ['latitude', 'longitude', 'location_name'],
            'classes': ['collapse'],
        }),
        ('İstatistikler', {
            'fields': ['response_count', 'question_count'],
        }),
    ]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'survey', 'question_type', 'is_required', 'order', 'response_count']
    list_filter = ['question_type', 'is_required', 'survey']
    search_fields = ['text', 'survey__title']
    inlines = [ChoiceInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'text_answer', 'number_answer', 'date_answer']


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['survey', 'respondent', 'is_complete', 'created_at', 'ip_address']
    list_filter = ['is_complete', 'created_at', 'survey']
    readonly_fields = ['session_id', 'ip_address', 'user_agent', 'completion_time']
    inlines = [AnswerInline]
