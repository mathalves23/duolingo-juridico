"""
Serializers para o serviço de IA do Duolingo Jurídico
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import (
    AIModel, AIRequest, LearningProfile, AdaptiveLearningSession,
    AIFeedback, ContentValidation, UserStudyRecommendation
)

User = get_user_model()


class AIModelSerializer(serializers.ModelSerializer):
    """Serializer para modelos de IA"""
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'model_type', 'provider', 'model_name',
            'api_endpoint', 'max_tokens', 'temperature', 'system_prompt',
            'cost_per_token', 'rate_limit_per_minute', 'is_active', 'is_default',
            'total_requests', 'total_tokens_used', 'average_response_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_requests', 'total_tokens_used', 'average_response_time',
            'created_at', 'updated_at'
        ]


class AIRequestSerializer(serializers.ModelSerializer):
    """Serializer para requisições de IA"""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = AIRequest
        fields = [
            'id', 'user', 'user_name', 'model', 'model_name', 'request_type',
            'context', 'input_text', 'output_text', 'tokens_used',
            'response_time_ms', 'cost', 'status', 'error_message',
            'retry_count', 'quality_score', 'user_feedback', 'is_helpful',
            'created_at', 'completed_at'
        ]
        read_only_fields = [
            'output_text', 'tokens_used', 'response_time_ms', 'cost',
            'status', 'error_message', 'retry_count', 'created_at', 'completed_at'
        ]
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        if 'user' not in validated_data:
            validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class LearningProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil de aprendizado"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    needs_update = serializers.SerializerMethodField()
    
    class Meta:
        model = LearningProfile
        fields = [
            'id', 'user', 'user_name', 'learning_style', 'difficulty_preference',
            'optimal_session_length', 'preferred_study_times', 'break_frequency',
            'subject_strengths', 'subject_weaknesses', 'question_type_performance',
            'common_mistakes', 'error_patterns', 'improvement_areas',
            'motivation_triggers', 'preferred_rewards', 'engagement_patterns',
            'content_complexity_level', 'explanation_detail_level', 'example_preference',
            'last_analysis', 'analysis_frequency_days',
            'needs_update', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'subject_strengths', 'subject_weaknesses', 'question_type_performance',
            'common_mistakes', 'error_patterns', 'improvement_areas',
            'last_analysis', 'created_at', 'updated_at'
        ]
    
    def get_needs_update(self, obj):
        return obj.needs_analysis_update()


class AdaptiveLearningSessionSerializer(serializers.ModelSerializer):
    """Serializer para sessões de aprendizado adaptativo"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    subject_name = serializers.CharField(source='target_subject.name', read_only=True)
    
    class Meta:
        model = AdaptiveLearningSession
        fields = [
            'id', 'user', 'user_name', 'session_type', 'target_subject',
            'subject_name', 'target_difficulty', 'content_selection_algorithm',
            'question_ordering_algorithm', 'initial_difficulty',
            'difficulty_adjustment_rate', 'performance_threshold',
            'questions_attempted', 'questions_correct', 'average_response_time',
            'final_difficulty', 'started_at', 'completed_at', 'is_completed',
            'performance_analysis', 'recommendations', 'next_session_suggestions',
            'accuracy_rate'
        ]
        read_only_fields = [
            'questions_attempted', 'questions_correct', 'average_response_time',
            'final_difficulty', 'started_at', 'completed_at', 'is_completed',
            'performance_analysis', 'recommendations', 'next_session_suggestions',
            'accuracy_rate'
        ]
    
    def create(self, validated_data):
        # Garantir que o usuário é o da requisição
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AIFeedbackSerializer(serializers.ModelSerializer):
    """Serializer para feedback de IA"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    question_title = serializers.CharField(source='question.title', read_only=True)
    ai_model_name = serializers.CharField(source='ai_model_used.name', read_only=True)
    
    class Meta:
        model = AIFeedback
        fields = [
            'id', 'user', 'user_name', 'feedback_type', 'context',
            'question', 'question_title', 'user_answer', 'session',
            'title', 'content', 'additional_resources', 'user_learning_style',
            'difficulty_level', 'tone', 'ai_confidence', 'user_rating',
            'was_helpful', 'user_feedback_text', 'ai_model_used',
            'ai_model_name', 'generation_time_ms', 'tokens_used', 'created_at'
        ]
        read_only_fields = [
            'ai_confidence', 'ai_model_used', 'generation_time_ms',
            'tokens_used', 'created_at'
        ]


class ContentValidationSerializer(serializers.ModelSerializer):
    """Serializer para validação de conteúdo"""
    
    ai_model_name = serializers.CharField(source='ai_model.name', read_only=True)
    question_title = serializers.CharField(source='question.title', read_only=True)
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)
    
    class Meta:
        model = ContentValidation
        fields = [
            'id', 'question', 'question_title', 'lesson', 'lesson_title',
            'legal_content', 'validation_type', 'status', 'confidence_score',
            'validation_details', 'issues_found', 'suggestions',
            'ai_model', 'ai_model_name', 'validated_at', 'content_last_modified'
        ]
        read_only_fields = [
            'confidence_score', 'validation_details', 'issues_found',
            'suggestions', 'validated_at'
        ]


class UserStudyRecommendationSerializer(serializers.ModelSerializer):
    """Serializer para recomendações de estudo"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    ai_model_name = serializers.CharField(source='ai_model.name', read_only=True)
    time_until_expires = serializers.SerializerMethodField()
    
    class Meta:
        model = UserStudyRecommendation
        fields = [
            'id', 'user', 'user_name', 'recommendation_type', 'priority',
            'title', 'description', 'reasoning', 'recommended_content',
            'estimated_time_minutes', 'optimal_timing', 'based_on_performance',
            'learning_profile_factors', 'is_active', 'was_followed',
            'user_feedback', 'effectiveness_score', 'ai_model', 'ai_model_name',
            'confidence_score', 'created_at', 'expires_at', 'followed_at',
            'is_expired', 'time_until_expires'
        ]
        read_only_fields = [
            'based_on_performance', 'learning_profile_factors', 'confidence_score',
            'created_at', 'followed_at', 'is_expired'
        ]
    
    def get_time_until_expires(self, obj):
        if obj.is_expired:
            return 0
        
        remaining = obj.expires_at - timezone.now()
        return max(0, int(remaining.total_seconds()))


# Serializers para estatísticas e dashboards
class AIUsageStatsSerializer(serializers.Serializer):
    """Serializer para estatísticas de uso da IA"""
    
    total_requests = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    failed_requests = serializers.IntegerField()
    average_response_time = serializers.FloatField()
    total_tokens_used = serializers.IntegerField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Por tipo de requisição
    requests_by_type = serializers.JSONField()
    
    # Por modelo
    usage_by_model = serializers.JSONField()
    
    # Qualidade
    average_quality_score = serializers.FloatField()
    user_satisfaction_rate = serializers.FloatField()


class LearningAnalyticsSerializer(serializers.Serializer):
    """Serializer para análise de aprendizado"""
    
    # Perfil do usuário
    learning_style = serializers.CharField()
    current_level = serializers.FloatField()
    improvement_rate = serializers.FloatField()
    
    # Performance por disciplina
    subject_performance = serializers.JSONField()
    
    # Padrões de estudo
    study_patterns = serializers.JSONField()
    optimal_study_times = serializers.JSONField()
    
    # Recomendações ativas
    active_recommendations = serializers.IntegerField()
    followed_recommendations = serializers.IntegerField()
    recommendation_effectiveness = serializers.FloatField()
    
    # Sessões adaptativas
    total_adaptive_sessions = serializers.IntegerField()
    average_session_improvement = serializers.FloatField()


# Serializers simplificados para listagens
class AIModelListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de modelos"""
    
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'model_type', 'provider', 'is_active',
            'is_default', 'total_requests'
        ]


class AIRequestListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de requisições"""
    
    model_name = serializers.CharField(source='model.name', read_only=True)
    
    class Meta:
        model = AIRequest
        fields = [
            'id', 'request_type', 'model_name', 'status',
            'tokens_used', 'response_time_ms', 'created_at'
        ]


class AIFeedbackListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de feedback"""
    
    class Meta:
        model = AIFeedback
        fields = [
            'id', 'feedback_type', 'title', 'user_rating',
            'was_helpful', 'created_at'
        ]


class UserStudyRecommendationListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de recomendações"""
    
    class Meta:
        model = UserStudyRecommendation
        fields = [
            'id', 'recommendation_type', 'priority', 'title',
            'is_active', 'was_followed', 'created_at', 'expires_at'
        ]


# Serializers para endpoints customizados
class QuestionExplanationRequestSerializer(serializers.Serializer):
    """Serializer para requisição de explicação de questão"""
    
    question_id = serializers.UUIDField()
    user_answer_id = serializers.UUIDField(required=False)
    explanation_style = serializers.ChoiceField(
        choices=[
            ('detailed', 'Detalhada'),
            ('simple', 'Simples'),
            ('step_by_step', 'Passo a Passo'),
            ('legal_focus', 'Foco Legal'),
        ],
        default='detailed'
    )
    include_references = serializers.BooleanField(default=True)
    user_context = serializers.JSONField(required=False)


class StudyRecommendationRequestSerializer(serializers.Serializer):
    """Serializer para requisição de recomendação de estudo"""
    
    focus_areas = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    available_time_minutes = serializers.IntegerField(default=30)
    difficulty_preference = serializers.ChoiceField(
        choices=[
            ('easy', 'Fácil'),
            ('medium', 'Médio'),
            ('hard', 'Difícil'),
            ('adaptive', 'Adaptativo'),
        ],
        default='adaptive'
    )
    session_type = serializers.ChoiceField(
        choices=[
            ('review', 'Revisão'),
            ('new_content', 'Novo Conteúdo'),
            ('practice', 'Prática'),
            ('weak_areas', 'Áreas Fracas'),
        ],
        default='adaptive'
    )
    target_subjects = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class FeedbackRatingSerializer(serializers.Serializer):
    """Serializer para avaliação de feedback"""
    
    rating = serializers.IntegerField(min_value=1, max_value=5)
    was_helpful = serializers.BooleanField()
    comment = serializers.CharField(max_length=500, required=False) 