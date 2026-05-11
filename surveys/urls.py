from django.urls import path

from . import views

app_name = 'surveys'

urlpatterns = [
    path('', views.survey_list, name='list'),
    path('my/', views.my_surveys, name='my_surveys'),
    path('<slug:slug>/', views.survey_detail, name='detail'),
    path('<slug:slug>/edit/', views.survey_edit, name='edit'),
    path('<slug:slug>/delete/', views.survey_delete, name='delete'),
    path('<slug:slug>/toggle-status/', views.survey_toggle_status, name='toggle_status'),
    path('<slug:slug>/add-question/', views.survey_add_question, name='add_question'),
    path('<slug:slug>/delete-question/<int:question_id>/', views.survey_delete_question, name='delete_question'),
    path('<slug:slug>/submit/', views.survey_submit, name='submit'),
    path('<slug:slug>/results/', views.survey_results, name='results'),
    path('<slug:slug>/results/json/', views.survey_results_json, name='results_json'),
]
