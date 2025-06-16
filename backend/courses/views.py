"""
Views para o sistema de cursos do Duolingo Jurídico
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta

from .models import (
    Subject, Topic, Lesson, UserLesson, 
    LegalContent, StudyPath, StudyPathSubject, UserStudyPath
)
from .serializers import (
    SubjectSerializer, SubjectListSerializer,
    TopicSerializer, TopicListSerializer,
    LessonSerializer, LessonListSerializer,
    UserLessonSerializer, LegalContentSerializer,
    StudyPathSerializer, UserStudyPathSerializer
)

User = get_user_model()


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet para disciplinas"""
    
    queryset = Subject.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SubjectListSerializer
        return SubjectSerializer
    
    def get_queryset(self):
        queryset = Subject.objects.filter(is_active=True)
        
        # Filtrar por categoria
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filtrar premium (apenas se usuário tem acesso)
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def topics(self, request, pk=None):
        """Listar tópicos de uma disciplina"""
        subject = self.get_object()
        topics = subject.topics.filter(is_active=True, parent_topic__isnull=True)
        
        if not getattr(request.user, 'is_premium', False):
            topics = topics.filter(is_premium=False)
        
        serializer = TopicListSerializer(
            topics.order_by('order'), 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """Progresso do usuário em uma disciplina"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        subject = self.get_object()
        
        # Estatísticas gerais
        total_lessons = Lesson.objects.filter(topic__subject=subject).count()
        completed_lessons = UserLesson.objects.filter(
            user=request.user,
            lesson__topic__subject=subject,
            completed=True
        ).count()
        
        # Progresso por tópico
        topics_progress = []
        for topic in subject.topics.filter(is_active=True):
            topic_total = topic.lessons.count()
            topic_completed = UserLesson.objects.filter(
                user=request.user,
                lesson__topic=topic,
                completed=True
            ).count()
            
            topics_progress.append({
                'topic_id': topic.id,
                'topic_name': topic.name,
                'total_lessons': topic_total,
                'completed_lessons': topic_completed,
                'progress_percentage': round((topic_completed / topic_total) * 100, 2) if topic_total > 0 else 0
            })
        
        # XP e moedas ganhas nesta disciplina
        user_lessons = UserLesson.objects.filter(
            user=request.user,
            lesson__topic__subject=subject,
            completed=True
        )
        total_xp = sum(ul.xp_earned for ul in user_lessons)
        total_coins = sum(ul.coins_earned for ul in user_lessons)
        
        return Response({
            'subject_id': subject.id,
            'subject_name': subject.name,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': round((completed_lessons / total_lessons) * 100, 2) if total_lessons > 0 else 0,
            'total_xp_earned': total_xp,
            'total_coins_earned': total_coins,
            'topics_progress': topics_progress
        })


class TopicViewSet(viewsets.ModelViewSet):
    """ViewSet para tópicos"""
    
    queryset = Topic.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = TopicSerializer
    
    def get_queryset(self):
        queryset = Topic.objects.filter(is_active=True)
        
        # Filtrar por disciplina
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)
        
        # Filtrar por tópico pai
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_topic_id=parent_id)
        elif parent_id != 'all':  # Se não especificado, apenas tópicos principais
            queryset = queryset.filter(parent_topic__isnull=True)
        
        # Filtrar premium
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('order', 'name')
    
    @action(detail=True, methods=['get'])
    def lessons(self, request, pk=None):
        """Listar lições de um tópico"""
        topic = self.get_object()
        lessons = topic.lessons.filter(is_active=True)
        
        if not getattr(request.user, 'is_premium', False):
            lessons = lessons.filter(is_premium=False)
        
        serializer = LessonListSerializer(
            lessons.order_by('order'), 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subtopics(self, request, pk=None):
        """Listar subtópicos"""
        topic = self.get_object()
        subtopics = topic.subtopics.filter(is_active=True)
        
        if not getattr(request.user, 'is_premium', False):
            subtopics = subtopics.filter(is_premium=False)
        
        serializer = TopicListSerializer(
            subtopics.order_by('order'), 
            many=True, 
            context={'request': request}
        )
        return Response(serializer.data)


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet para lições"""
    
    queryset = Lesson.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LessonListSerializer
        return LessonSerializer
    
    def get_queryset(self):
        queryset = Lesson.objects.filter(is_active=True)
        
        # Filtrar por tópico
        topic_id = self.request.query_params.get('topic')
        if topic_id:
            queryset = queryset.filter(topic_id=topic_id)
        
        # Filtrar por disciplina
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(topic__subject_id=subject_id)
        
        # Filtrar por tipo
        lesson_type = self.request.query_params.get('type')
        if lesson_type:
            queryset = queryset.filter(lesson_type=lesson_type)
        
        # Filtrar por dificuldade
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filtrar premium
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        return queryset.order_by('topic__order', 'order', 'title')
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Iniciar uma lição"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        lesson = self.get_object()
        
        # Verificar se a lição está desbloqueada
        # TODO: Implementar lógica de desbloqueio baseada em pré-requisitos
        
        # Criar ou obter progresso do usuário
        user_lesson, created = UserLesson.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        if not created:
            user_lesson.attempts += 1
            user_lesson.save()
        
        serializer = UserLessonSerializer(user_lesson, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar uma lição"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        lesson = self.get_object()
        score = request.data.get('score', 0)
        
        # Validar pontuação
        if not isinstance(score, (int, float)) or score < 0 or score > 100:
            return Response({'error': 'Pontuação deve ser entre 0 e 100'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Obter ou criar progresso do usuário
        user_lesson, created = UserLesson.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        
        # Marcar como completada
        user_lesson.mark_completed(score)
        
        # Atualizar estatísticas da lição
        lesson.update_completion_stats()
        
        # Atualizar gamificação do usuário
        user = request.user
        user.total_xp += user_lesson.xp_earned
        user.total_coins += user_lesson.coins_earned
        user.save()
        
        serializer = UserLessonSerializer(user_lesson, context={'request': request})
        return Response({
            'user_lesson': serializer.data,
            'rewards': {
                'xp_earned': user_lesson.xp_earned,
                'coins_earned': user_lesson.coins_earned,
                'new_total_xp': user.total_xp,
                'new_total_coins': user.total_coins
            }
        })
    
    @action(detail=False, methods=['get'])
    def review_due(self, request):
        """Lições que precisam de revisão"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        # Lições que precisam de revisão hoje
        today = timezone.now().date()
        review_lessons = UserLesson.objects.filter(
            user=request.user,
            completed=True,
            next_review_date__lte=today
        ).select_related('lesson', 'lesson__topic', 'lesson__topic__subject')
        
        lessons_data = []
        for user_lesson in review_lessons:
            lessons_data.append({
                'user_lesson_id': user_lesson.id,
                'lesson': LessonListSerializer(
                    user_lesson.lesson, 
                    context={'request': request}
                ).data,
                'next_review_date': user_lesson.next_review_date,
                'review_interval_days': user_lesson.review_interval_days
            })
        
        return Response({
            'total_reviews': len(lessons_data),
            'lessons': lessons_data
        })


class UserLessonViewSet(viewsets.ModelViewSet):
    """ViewSet para progresso do usuário"""
    
    serializer_class = UserLessonSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserLesson.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas do usuário"""
        user_lessons = self.get_queryset()
        
        # Estatísticas gerais
        total_started = user_lessons.count()
        total_completed = user_lessons.filter(completed=True).count()
        total_xp = sum(ul.xp_earned for ul in user_lessons)
        total_coins = sum(ul.coins_earned for ul in user_lessons)
        
        # Média de pontuação
        completed_lessons = user_lessons.filter(completed=True)
        avg_score = completed_lessons.aggregate(avg=Avg('score'))['avg'] or 0.0
        
        # Atividade recente (últimos 7 dias)
        week_ago = timezone.now() - timedelta(days=7)
        recent_activity = user_lessons.filter(
            completed_at__gte=week_ago
        ).count()
        
        # Progresso por disciplina
        subjects_progress = {}
        for user_lesson in completed_lessons:
            subject_name = user_lesson.lesson.topic.subject.name
            if subject_name not in subjects_progress:
                subjects_progress[subject_name] = {
                    'completed_lessons': 0,
                    'total_xp': 0,
                    'total_coins': 0
                }
            
            subjects_progress[subject_name]['completed_lessons'] += 1
            subjects_progress[subject_name]['total_xp'] += user_lesson.xp_earned
            subjects_progress[subject_name]['total_coins'] += user_lesson.coins_earned
        
        return Response({
            'total_started': total_started,
            'total_completed': total_completed,
            'completion_rate': round((total_completed / total_started) * 100, 2) if total_started > 0 else 0,
            'total_xp_earned': total_xp,
            'total_coins_earned': total_coins,
            'average_score': round(avg_score, 2),
            'recent_activity_count': recent_activity,
            'subjects_progress': subjects_progress
        })


class LegalContentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para conteúdo jurídico"""
    
    queryset = LegalContent.objects.filter(is_current=True)
    serializer_class = LegalContentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo de conteúdo
        content_type = self.request.query_params.get('type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filtrar por disciplina
        subject_id = self.request.query_params.get('subject')
        if subject_id:
            queryset = queryset.filter(subjects__id=subject_id)
        
        # Busca por texto
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(official_number__icontains=search) |
                Q(summary__icontains=search)
            )
        
        return queryset.order_by('-publication_date', 'title')


class StudyPathViewSet(viewsets.ModelViewSet):
    """ViewSet para trilhas de estudo"""
    
    queryset = StudyPath.objects.filter(is_public=True)
    serializer_class = StudyPathSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por nível de dificuldade
        difficulty = self.request.query_params.get('difficulty')
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        
        # Filtrar por exame alvo
        exam = self.request.query_params.get('exam')
        if exam:
            queryset = queryset.filter(target_exam__icontains=exam)
        
        # Filtrar premium
        if not getattr(self.request.user, 'is_premium', False):
            queryset = queryset.filter(is_premium=False)
        
        # Ordenar por popularidade
        return queryset.order_by('-enrollment_count', 'name')
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Matricular-se em uma trilha"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        study_path = self.get_object()
        target_date = request.data.get('target_completion_date')
        
        if not target_date:
            return Response({'error': 'Data alvo é obrigatória'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar se já está matriculado
        if UserStudyPath.objects.filter(
            user=request.user, 
            study_path=study_path
        ).exists():
            return Response({'error': 'Já matriculado nesta trilha'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Criar matrícula
        enrollment = UserStudyPath.objects.create(
            user=request.user,
            study_path=study_path,
            target_completion_date=target_date
        )
        
        # Atualizar contador de matrículas
        study_path.enrollment_count += 1
        study_path.save()
        
        serializer = UserStudyPathSerializer(enrollment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def unenroll(self, request, pk=None):
        """Desmatricular-se de uma trilha"""
        if not request.user.is_authenticated:
            return Response({'error': 'Autenticação necessária'}, 
                          status=status.HTTP_401_UNAUTHORIZED)
        
        study_path = self.get_object()
        
        try:
            enrollment = UserStudyPath.objects.get(
                user=request.user,
                study_path=study_path
            )
            enrollment.delete()
            
            # Atualizar contador de matrículas
            if study_path.enrollment_count > 0:
                study_path.enrollment_count -= 1
                study_path.save()
            
            return Response({'message': 'Desmatrícula realizada com sucesso'})
        
        except UserStudyPath.DoesNotExist:
            return Response({'error': 'Não matriculado nesta trilha'}, 
                          status=status.HTTP_404_NOT_FOUND)


class UserStudyPathViewSet(viewsets.ModelViewSet):
    """ViewSet para matrículas do usuário"""
    
    serializer_class = UserStudyPathSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return UserStudyPath.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def update_progress(self, request, pk=None):
        """Atualizar progresso em uma trilha"""
        enrollment = self.get_object()
        enrollment.update_progress()
        
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data)
