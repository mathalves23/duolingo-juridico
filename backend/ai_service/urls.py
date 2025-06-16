"""
URLs para serviços de IA
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIModelViewSet, AIRequestViewSet, LearningProfileViewSet,
    AdaptiveLearningSessionViewSet, AIFeedbackViewSet, ContentValidationViewSet, 
    UserStudyRecommendationViewSet, AIAnalyticsView,
    generate_explanation, get_study_recommendations, 
    analyze_performance, generate_quiz_suggestions, chat_with_tutor
)

router = DefaultRouter()
router.register(r'models', AIModelViewSet, basename='aimodel')
router.register(r'requests', AIRequestViewSet, basename='airequest')
router.register(r'profiles', LearningProfileViewSet, basename='learningprofile')
router.register(r'sessions', AdaptiveLearningSessionViewSet, basename='adaptivelearningsession')
router.register(r'feedback', AIFeedbackViewSet, basename='aifeedback')
router.register(r'content-validation', ContentValidationViewSet, basename='contentvalidation')
router.register(r'recommendations', UserStudyRecommendationViewSet, basename='studyrecommendation')
router.register(r'analytics', AIAnalyticsView, basename='aianalytics')

urlpatterns = [
    path('', include(router.urls)),
    
    # Endpoints de IA personalizada
    path('explain/', generate_explanation, name='generate_explanation'),
    path('recommendations/', get_study_recommendations, name='study_recommendations'),
    path('analyze/', analyze_performance, name='analyze_performance'),
    path('suggestions/', generate_quiz_suggestions, name='quiz_suggestions'),
    path('tutor/', chat_with_tutor, name='chat_tutor'),
] 