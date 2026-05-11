"""
Sahaflar Platformu — API Views
RESTful API viewsets with proper permissions.
"""
from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response as DRFResponse

from surveys.models import Category, Survey, Question, Response
from .serializers import (
    UserSerializer, CategorySerializer,
    SurveyListSerializer, SurveyDetailSerializer,
    ResponseSerializer,
)

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission: only owner can modify."""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.creator == request.user


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for survey categories."""
    queryset = Category.objects.annotate(survey_count=Count('surveys'))
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class SurveyViewSet(viewsets.ModelViewSet):
    """
    API endpoint for surveys.
    - GET: List/retrieve surveys (public)
    - POST: Create survey (authenticated)
    - PUT/PATCH: Update survey (owner only)
    - DELETE: Delete survey (owner only)
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SurveyDetailSerializer
        return SurveyListSerializer

    def get_queryset(self):
        queryset = Survey.objects.select_related('creator', 'category').annotate(
            total_responses=Count('responses')
        )
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True, status=Survey.Status.ACTIVE)
        return queryset

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get survey results as JSON."""
        survey = self.get_object()
        questions = survey.questions.prefetch_related('choices').all()

        data = []
        for question in questions:
            q_data = {
                'id': question.id,
                'text': question.text,
                'type': question.question_type,
                'choices': [],
            }
            for choice in question.choices.all():
                q_data['choices'].append({
                    'text': choice.text,
                    'count': choice.selected_answers.count(),
                    'percentage': choice.percentage,
                })
            data.append(q_data)

        return DRFResponse({
            'survey': survey.title,
            'total_responses': survey.responses.filter(is_complete=True).count(),
            'questions': data,
        })

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def submit(self, request, pk=None):
        """Submit a response to a survey."""
        survey = self.get_object()
        if not survey.can_respond(request.user if request.user.is_authenticated else None):
            return DRFResponse(
                {'error': 'Bu ankete yanıt veremezsiniz.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ResponseSerializer(data={
            'survey': survey.id,
            **request.data
        })
        if serializer.is_valid():
            serializer.save(
                respondent=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                is_complete=True,
            )
            return DRFResponse(serializer.data, status=status.HTTP_201_CREATED)
        return DRFResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for user information (read-only)."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
