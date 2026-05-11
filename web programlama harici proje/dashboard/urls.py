from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('map/', views.map_view, name='map'),
    path('builder/', views.survey_builder, name='builder'),
    path('settings/', views.settings_view, name='settings'),
    path('export/all/', views.export_all_csv, name='export_all'),
    path('export/<slug:slug>/', views.export_csv, name='export_survey'),
]
