"""
Views para o sistema de questões e simulados do Duolingo Jurídico
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, F, Max
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random

from .models import (
    ExamBoard, Question, QuestionOption, QuestionExplanation,
    UserAnswer, Quiz, QuizAttempt, QuestionReport
)
from .serializers import (
    ExamBoardSerializer, ExamBoardListSerializer,
    QuestionSerializer, QuestionListSerializer,
    UserAnswerSerializer, QuizSerializer, QuizListSerializer,
    QuizAttemptSerializer, QuestionReportSerializer,
    QuestionStatsSerializer, QuizStatsSerializer
)

User = get_user_model()


class ExamBoardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para bancas examinadoras"""
    
    queryset = ExamBoard.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ExamBoardListSerializer
        return ExamBoardSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Busca por nome ou sigla
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(acronym__icontains=search)
            )
        
        return queryset.order_by('name')


class QuestionViewSet(viewsets.ModelViewSet):
    """ViewSet para questões"""
    
    queryset = Question.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuestionListSerializer
        return QuestionSerializer
    
    def get_queryset(self):
        queryset = Question.objects.filter(is_active=True, reviewed=True)
        
        # Filtros básicos
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        exam_board_id = self.request.query_params.get('exam_board')
        if exam_board_id:
            queryset = queryset.filter(exam_board_id=exam_board_id)
        
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        question_type = self.request.query_params.get('type')
        if question_type:
            queryset = queryset.filter(question_type=question_type)
        
        # Filtrar premium
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('-exam_year', 'exam_name')
    
    @action(detail=True, methods=['post'])
    def answer(self, request, pk=None):
        """Responder uma questão"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        question = self.get_object()
        
        # Verificar se já respondeu
        existing_answer = UserAnswer.objects.filter(
            user=request.user,
            question=question
        ).first()
        
        if existing_answer:
            return Response({'error': 'Questão já foi respondida'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Criar resposta
        serializer = UserAnswerSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user_answer = serializer.save()
            
            # Atualizar estatísticas da questão
            question.update_statistics()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAnswerViewSet(viewsets.ModelViewSet):
    """ViewSet para respostas dos usuários"""
    
    serializer_class = UserAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserAnswer.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das respostas do usuário"""
        user_answers = self.get_queryset()
        
        total_answers = user_answers.count()
        correct_answers = user_answers.filter(is_correct=True).count()
        accuracy_rate = (correct_answers / total_answers * 100) if total_answers > 0 else 0
        
        return Response({
            'total_answers': total_answers,
            'correct_answers': correct_answers,
            'accuracy_rate': round(accuracy_rate, 2)
        })


class QuizViewSet(viewsets.ModelViewSet):
    """ViewSet para quizzes e simulados"""
    
    queryset = Quiz.objects.filter(status='published')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return QuizListSerializer
        return QuizSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar premium
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('-total_attempts', 'title')
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar um quiz"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        quiz = self.get_object()
        
        # Criar nova tentativa
        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz
        )
        
        serializer = QuizAttemptSerializer(attempt)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """ViewSet para tentativas de quiz"""
    
    serializer_class = QuizAttemptSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar uma tentativa de quiz"""
        attempt = self.get_object()
        
        if attempt.status != 'in_progress':
            return Response({'error': 'Tentativa já finalizada'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Completar tentativa
        attempt.complete_attempt()
        
        serializer = self.get_serializer(attempt)
        return Response(serializer.data)


class QuestionReportViewSet(viewsets.ModelViewSet):
    """ViewSet para denúncias de questões"""
    
    serializer_class = QuestionReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_staff:
            return QuestionReport.objects.filter(user=self.request.user)
        return QuestionReport.objects.all() 