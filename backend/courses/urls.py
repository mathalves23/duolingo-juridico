"""
URLs para cursos e conteúdo educacional
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, TopicViewSet, LessonViewSet,
    UserLessonViewSet, LegalContentViewSet,
    StudyPathViewSet, UserStudyPathViewSet
)

router = DefaultRouter()

# Registrar ViewSets
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'user-lessons', UserLessonViewSet, basename='user-lesson')
router.register(r'legal-content', LegalContentViewSet, basename='legal-content')
router.register(r'study-paths', StudyPathViewSet, basename='study-path')
router.register(r'my-study-paths', UserStudyPathViewSet, basename='user-study-path')

urlpatterns = [
    path('', include(router.urls)),
] 