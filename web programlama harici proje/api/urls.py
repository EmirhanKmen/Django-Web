from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api'

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'surveys', views.SurveyViewSet, basename='survey')
router.register(r'users', views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
