"""
Sahaflar Platformu — API Serializers
RESTful API serializers for all platform models.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from surveys.models import Category, Survey, Question, Choice, Response, Answer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Public user information serializer."""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role',
                  'organization', 'is_verified', 'date_joined']
        read_only_fields = fields


class CategorySerializer(serializers.ModelSerializer):
    survey_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'color', 'survey_count']


class ChoiceSerializer(serializers.ModelSerializer):
    vote_count = serializers.IntegerField(read_only=True, default=0)
    percentage = serializers.FloatField(read_only=True, default=0)

    class Meta:
        model = Choice
        fields = ['id', 'text', 'order', 'vote_count', 'percentage']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'question_type', 'is_required', 'order',
                  'help_text', 'min_value', 'max_value', 'choices']


class SurveyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for survey lists."""
    creator = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    response_count = serializers.IntegerField(read_only=True)
    question_count = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'slug', 'description', 'creator', 'category',
                  'status', 'priority', 'pub_date', 'expires_at',
                  'is_public', 'response_count', 'question_count', 'is_active',
                  'location_name', 'created_at']


class SurveyDetailSerializer(serializers.ModelSerializer):
    """Full serializer with questions and choices."""
    creator = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)
    response_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Survey
        fields = ['id', 'title', 'slug', 'description', 'creator', 'category',
                  'status', 'priority', 'pub_date', 'expires_at',
                  'is_public', 'allow_anonymous', 'require_location',
                  'max_responses', 'response_count', 'questions',
                  'latitude', 'longitude', 'location_name', 'created_at']


class AnswerSerializer(serializers.ModelSerializer):
    selected_choices = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Choice.objects.all(), required=False
    )

    class Meta:
        model = Answer
        fields = ['question', 'text_answer', 'number_answer', 'selected_choices', 'date_answer']


class ResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Response
        fields = ['id', 'survey', 'latitude', 'longitude', 'answers', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        response = Response.objects.create(**validated_data)
        for answer_data in answers_data:
            choices = answer_data.pop('selected_choices', [])
            answer = Answer.objects.create(response=response, **answer_data)
            if choices:
                answer.selected_choices.set(choices)
        return response
