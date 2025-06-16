"""
URLs para questões e quizzes
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamBoardViewSet, QuestionViewSet, UserAnswerViewSet,
    QuizViewSet, QuizAttemptViewSet, QuestionReportViewSet
)

router = DefaultRouter()

# Registrar ViewSets
router.register(r'exam-boards', ExamBoardViewSet, basename='exam-board')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'user-answers', UserAnswerViewSet, basename='user-answer')
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'quiz-attempts', QuizAttemptViewSet, basename='quiz-attempt')
router.register(r'question-reports', QuestionReportViewSet, basename='question-report')

urlpatterns = [
    path('', include(router.urls)),
] 