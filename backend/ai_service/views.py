"""
Views para o serviço de IA do Duolingo Jurídico
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.conf import settings
import openai
import json
from typing import Dict, List, Any

from .models import (
    AIModel, AIRequest, LearningProfile, AdaptiveLearningSession,
    AIFeedback, ContentValidation, UserStudyRecommendation
)
from .serializers import (
    AIModelSerializer, AIModelListSerializer,
    AIRequestSerializer, AIRequestListSerializer,
    LearningProfileSerializer, AdaptiveLearningSessionSerializer,
    AIFeedbackSerializer, AIFeedbackListSerializer,
    ContentValidationSerializer, UserStudyRecommendationSerializer,
    UserStudyRecommendationListSerializer, AIUsageStatsSerializer,
    LearningAnalyticsSerializer, QuestionExplanationRequestSerializer,
    StudyRecommendationRequestSerializer, FeedbackRatingSerializer
)

User = get_user_model()

# Configurar OpenAI (em produção, usar variável de ambiente)
openai.api_key = getattr(settings, 'OPENAI_API_KEY', 'your-openai-key-here')


class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para modelos de IA (apenas leitura para usuários)"""
    
    queryset = AIModel.objects.filter(is_active=True)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AIModelListSerializer
        return AIModelSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        model_type = self.request.query_params.get('type')
        if model_type:
            queryset = queryset.filter(model_type=model_type)
        
        # Filtrar por provedor
        provider = self.request.query_params.get('provider')
        if provider:
            queryset = queryset.filter(provider=provider)
        
        return queryset.order_by('model_type', 'name')
    
    @action(detail=False, methods=['get'])
    def default_models(self, request):
        """Obter modelos padrão por tipo"""
        default_models = {}
        
        for model_type, _ in AIModel.MODEL_TYPES:
            default_model = AIModel.objects.filter(
                model_type=model_type,
                is_active=True,
                is_default=True
            ).first()
            
            if default_model:
                default_models[model_type] = AIModelListSerializer(default_model).data
        
        return Response(default_models)


class AIRequestViewSet(viewsets.ModelViewSet):
    """ViewSet para requisições de IA"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AIRequestListSerializer
        return AIRequestSerializer
    
    def get_queryset(self):
        # Usuários veem apenas suas próprias requisições
        queryset = AIRequest.objects.filter(user=self.request.user)
        
        # Filtros
        request_type = self.request.query_params.get('type')
        if request_type:
            queryset = queryset.filter(request_type=request_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das requisições do usuário"""
        user_requests = self.get_queryset()
        
        # Estatísticas gerais
        total_requests = user_requests.count()
        successful_requests = user_requests.filter(status='completed').count()
        failed_requests = user_requests.filter(status='failed').count()
        
        # Estatísticas por tipo
        requests_by_type = {}
        for req_type, _ in AIRequest.REQUEST_TYPES:
            count = user_requests.filter(request_type=req_type).count()
            if count > 0:
                requests_by_type[req_type] = count
        
        # Custos e tokens
        total_tokens = user_requests.aggregate(
            total=Sum('tokens_used')
        )['total'] or 0
        
        total_cost = user_requests.aggregate(
            total=Sum('cost')
        )['total'] or 0
        
        # Tempo médio de resposta
        avg_response_time = user_requests.filter(
            status='completed'
        ).aggregate(avg=Avg('response_time_ms'))['avg'] or 0
        
        return Response({
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': round(
                (successful_requests / total_requests) * 100, 2
            ) if total_requests > 0 else 0,
            'requests_by_type': requests_by_type,
            'total_tokens_used': total_tokens,
            'total_cost': float(total_cost),
            'average_response_time_ms': round(avg_response_time, 2)
        })


class LearningProfileViewSet(viewsets.ModelViewSet):
    """ViewSet para perfis de aprendizado"""
    
    serializer_class = LearningProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return LearningProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        # Sempre retornar/criar o perfil do usuário atual
        profile, created = LearningProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """Analisar performance e atualizar perfil"""
        profile = self.get_object()
        
        # Analisar performance do usuário
        user = request.user
        
        # Análise por disciplina
        subject_performance = {}
        for answer in user.user_answers.select_related('question__subject'):
            subject_name = answer.question.subject.name
            subject_id = answer.question.subject.id
            
            if subject_id not in subject_performance:
                subject_performance[subject_id] = {
                    'total': 0,
                    'correct': 0,
                    'avg_time': 0,
                    'total_time': 0
                }
            
            subject_performance[subject_id]['total'] += 1
            if answer.is_correct:
                subject_performance[subject_id]['correct'] += 1
            subject_performance[subject_id]['total_time'] += answer.time_spent
        
        # Calcular forças e fraquezas
        strengths = {}
        weaknesses = {}
        
        for subject_id, perf in subject_performance.items():
            accuracy = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            avg_time = perf['total_time'] / perf['total'] if perf['total'] > 0 else 0
            
            if accuracy >= 80:
                strengths[subject_id] = {
                    'accuracy': round(accuracy, 2),
                    'avg_time': round(avg_time, 2)
                }
            elif accuracy < 60:
                weaknesses[subject_id] = {
                    'accuracy': round(accuracy, 2),
                    'avg_time': round(avg_time, 2),
                    'needs_improvement': True
                }
        
        # Atualizar perfil
        profile.subject_strengths = strengths
        profile.subject_weaknesses = weaknesses
        profile.last_analysis = timezone.now()
        profile.save()
        
        serializer = self.get_serializer(profile)
        return Response({
            'profile': serializer.data,
            'analysis_summary': {
                'total_subjects_analyzed': len(subject_performance),
                'strong_subjects': len(strengths),
                'weak_subjects': len(weaknesses),
                'overall_accuracy': round(
                    sum(perf['correct'] for perf in subject_performance.values()) /
                    sum(perf['total'] for perf in subject_performance.values()) * 100, 2
                ) if subject_performance else 0
            }
        })


class AdaptiveLearningSessionViewSet(viewsets.ModelViewSet):
    """ViewSet para sessões de aprendizado adaptativo"""
    
    serializer_class = AdaptiveLearningSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AdaptiveLearningSession.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Completar uma sessão adaptativa"""
        session = self.get_object()
        
        if session.is_completed:
            return Response({'error': 'Sessão já foi completada'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Completar sessão
        session.complete_session()
        
        serializer = self.get_serializer(session)
        return Response({
            'session': serializer.data,
            'performance_summary': {
                'accuracy_rate': session.accuracy_rate,
                'improvement': session.final_difficulty - session.initial_difficulty
                if session.final_difficulty else 0,
                'recommendations': session.recommendations
            }
        })
    
    @action(detail=False, methods=['post'])
    def create_adaptive(self, request):
        """Criar sessão adaptativa personalizada"""
        user = request.user
        subject_id = request.data.get('subject_id')
        session_type = request.data.get('session_type', 'practice')
        
        if not subject_id:
            return Response({'error': 'ID da disciplina é obrigatório'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Obter perfil de aprendizado
        try:
            profile = user.learning_profile
        except LearningProfile.DoesNotExist:
            profile = LearningProfile.objects.create(user=user)
        
        # Calcular dificuldade alvo baseada no perfil
        target_difficulty = profile.content_complexity_level
        
        # Criar sessão
        session = AdaptiveLearningSession.objects.create(
            user=user,
            session_type=session_type,
            target_subject_id=subject_id,
            target_difficulty=target_difficulty,
            initial_difficulty=target_difficulty
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AIFeedbackViewSet(viewsets.ModelViewSet):
    """ViewSet para feedback de IA"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AIFeedbackListSerializer
        return AIFeedbackSerializer
    
    def get_queryset(self):
        return AIFeedback.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Avaliar feedback de IA"""
        feedback = self.get_object()
        
        serializer = FeedbackRatingSerializer(data=request.data)
        if serializer.is_valid():
            feedback.user_rating = serializer.validated_data['rating']
            feedback.was_helpful = serializer.validated_data['was_helpful']
            feedback.user_feedback_text = serializer.validated_data.get('comment', '')
            feedback.save()
            
            return Response({'message': 'Avaliação registrada com sucesso'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def request_explanation(self, request):
        """Solicitar explicação de questão via IA"""
        serializer = QuestionExplanationRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            # Criar requisição de IA para explicação
            # (Implementação simplificada - em produção integraria com serviço de IA real)
            
            ai_request = AIRequest.objects.create(
                user=request.user,
                model=AIModel.objects.filter(
                    model_type='explanation',
                    is_active=True
                ).first(),
                request_type='explanation',
                input_text=f"Explicar questão {serializer.validated_data['question_id']}",
                context=serializer.validated_data
            )
            
            # Simular resposta da IA (em produção seria assíncrono)
            ai_request.output_text = "Explicação detalhada da questão..."
            ai_request.status = 'completed'
            ai_request.completed_at = timezone.now()
            ai_request.save()
            
            # Criar feedback
            feedback = AIFeedback.objects.create(
                user=request.user,
                feedback_type='answer_explanation',
                context='question_explanation',
                title='Explicação da Questão',
                content=ai_request.output_text,
                ai_model_used=ai_request.model,
                ai_confidence=0.85
            )
            
            feedback_serializer = AIFeedbackSerializer(feedback)
            return Response(feedback_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentValidationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para validações de conteúdo (apenas leitura)"""
    
    serializer_class = ContentValidationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = ContentValidation.objects.all()
        
        # Filtros
        validation_type = self.request.query_params.get('type')
        if validation_type:
            queryset = queryset.filter(validation_type=validation_type)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-validated_at')


class UserStudyRecommendationViewSet(viewsets.ModelViewSet):
    """ViewSet para recomendações de estudo"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return UserStudyRecommendationListSerializer
        return UserStudyRecommendationSerializer
    
    def get_queryset(self):
        queryset = UserStudyRecommendation.objects.filter(user=self.request.user)
        
        # Filtros
        is_active = self.request.query_params.get('active')
        if is_active == 'true':
            queryset = queryset.filter(is_active=True, expires_at__gt=timezone.now())
        elif is_active == 'false':
            queryset = queryset.filter(
                Q(is_active=False) | Q(expires_at__lte=timezone.now())
            )
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-priority', '-created_at')
    
    @action(detail=True, methods=['post'])
    def follow(self, request, pk=None):
        """Marcar recomendação como seguida"""
        recommendation = self.get_object()
        
        if recommendation.was_followed:
            return Response({'error': 'Recomendação já foi seguida'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        recommendation.mark_followed()
        
        serializer = self.get_serializer(recommendation)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def generate_recommendations(self, request):
        """Gerar novas recomendações de estudo"""
        user = request.user
        
        serializer = StudyRecommendationRequestSerializer(data=request.data)
        if serializer.is_valid():
            # Gerar recomendações baseadas no perfil do usuário
            # (Implementação simplificada)
            
            recommendations = []
            
            # Recomendação de revisão baseada em performance
            if user.user_lessons.filter(completed=True).exists():
                weak_subjects = []
                
                # Analisar disciplinas com baixa performance
                for answer in user.user_answers.select_related('question__subject'):
                    subject = answer.question.subject
                    # Lógica simplificada para identificar áreas fracas
                    
                recommendation = UserStudyRecommendation.objects.create(
                    user=user,
                    recommendation_type='review_session',
                    priority='high',
                    title='Revisão de Áreas Fracas',
                    description='Recomendamos revisar os tópicos com menor taxa de acerto.',
                    reasoning='Baseado na análise de sua performance recente.',
                    ai_model=AIModel.objects.filter(
                        model_type='adaptive_learning'
                    ).first(),
                    expires_at=timezone.now() + timedelta(days=7),
                    confidence_score=0.8
                )
                recommendations.append(recommendation)
            
            # Serializar recomendações
            recommendations_serializer = UserStudyRecommendationSerializer(
                recommendations, 
                many=True,
                context={'request': request}
            )
            
            return Response({
                'generated_recommendations': len(recommendations),
                'recommendations': recommendations_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estatísticas das recomendações do usuário"""
        recommendations = self.get_queryset()
        
        total_recommendations = recommendations.count()
        followed_recommendations = recommendations.filter(was_followed=True).count()
        active_recommendations = recommendations.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        # Efetividade por tipo
        effectiveness_by_type = {}
        for rec_type, _ in UserStudyRecommendation.RECOMMENDATION_TYPES:
            type_recs = recommendations.filter(recommendation_type=rec_type)
            followed = type_recs.filter(was_followed=True).count()
            total = type_recs.count()
            
            if total > 0:
                effectiveness_by_type[rec_type] = {
                    'total': total,
                    'followed': followed,
                    'follow_rate': round((followed / total) * 100, 2)
                }
        
        return Response({
            'total_recommendations': total_recommendations,
            'followed_recommendations': followed_recommendations,
            'active_recommendations': active_recommendations,
            'follow_rate': round(
                (followed_recommendations / total_recommendations) * 100, 2
            ) if total_recommendations > 0 else 0,
            'effectiveness_by_type': effectiveness_by_type
        })


# Views para endpoints customizados de IA
class AIAnalyticsView(viewsets.ViewSet):
    """ViewSet para análises e estatísticas de IA"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def learning_analytics(self, request):
        """Análise completa de aprendizado do usuário"""
        user = request.user
        
        # Obter perfil de aprendizado
        try:
            profile = user.learning_profile
        except LearningProfile.DoesNotExist:
            profile = LearningProfile.objects.create(user=user)
        
        # Calcular nível atual baseado na performance
        total_answers = user.user_answers.count()
        correct_answers = user.user_answers.filter(is_correct=True).count()
        current_level = (correct_answers / total_answers) * 5 if total_answers > 0 else 1.0
        
        # Taxa de melhoria (comparar últimos 30 dias com anteriores)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_answers = user.user_answers.filter(answered_at__gte=thirty_days_ago)
        older_answers = user.user_answers.filter(answered_at__lt=thirty_days_ago)
        
        recent_accuracy = (
            recent_answers.filter(is_correct=True).count() / 
            recent_answers.count()
        ) * 100 if recent_answers.exists() else 0
        
        older_accuracy = (
            older_answers.filter(is_correct=True).count() / 
            older_answers.count()
        ) * 100 if older_answers.exists() else 0
        
        improvement_rate = recent_accuracy - older_accuracy
        
        # Recomendações ativas
        active_recs = user.study_recommendations.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        followed_recs = user.study_recommendations.filter(
            was_followed=True
        ).count()
        
        total_recs = user.study_recommendations.count()
        
        analytics_data = {
            'learning_style': profile.learning_style,
            'current_level': round(current_level, 2),
            'improvement_rate': round(improvement_rate, 2),
            'subject_performance': profile.subject_strengths,
            'study_patterns': {
                'optimal_session_length': profile.optimal_session_length,
                'preferred_study_times': profile.preferred_study_times,
                'break_frequency': profile.break_frequency
            },
            'optimal_study_times': profile.preferred_study_times,
            'active_recommendations': active_recs,
            'followed_recommendations': followed_recs,
            'recommendation_effectiveness': round(
                (followed_recs / total_recs) * 100, 2
            ) if total_recs > 0 else 0,
            'total_adaptive_sessions': user.adaptive_sessions.count(),
            'average_session_improvement': 0.0  # Calcular baseado nas sessões
        }
        
        serializer = LearningAnalyticsSerializer(data=analytics_data)
        serializer.is_valid()
        return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_explanation(request):
    """
    Gera explicação personalizada para uma questão usando IA
    """
    try:
        data = request.data
        question_text = data.get('question_text', '')
        correct_answer = data.get('correct_answer', '')
        user_answer = data.get('user_answer', '')
        subject = data.get('subject', '')
        
        if not question_text or not correct_answer:
            return Response(
                {'error': 'question_text e correct_answer são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prompt para gerar explicação
        prompt = f"""
        Como um professor especialista em concursos públicos brasileiros, explique de forma didática:

        Disciplina: {subject}
        Questão: {question_text}
        Resposta Correta: {correct_answer}
        {f"Resposta do Estudante: {user_answer}" if user_answer else ""}

        Forneça uma explicação clara e educativa que:
        1. Explique por que a resposta correta está certa
        2. {f"Explique o erro na resposta escolhida pelo estudante" if user_answer and user_answer != correct_answer else ""}
        3. Dê dicas para não errar questões similares
        4. Cite a base legal ou conceitual quando aplicável
        
        Seja conciso mas completo, usando linguagem acessível.
        """
        
        # Simular resposta da OpenAI (em produção, usar a API real)
        if hasattr(openai, 'ChatCompletion') and False:  # Desabilitado para demo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um professor especialista em concursos públicos brasileiros."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            explanation = response.choices[0].message.content
        else:
            # Mock explanation para demonstração
            explanation = f"""
            **Explicação da Questão:**
            
            A resposta correta é "{correct_answer}" porque esta alternativa está em conformidade com os princípios fundamentais 
            estabelecidos pela Constituição Federal de 1988.
            
            **Fundamentação Legal:**
            Esta questão se baseia no Art. 1º da CF/88, que estabelece os fundamentos da República Federativa do Brasil, 
            incluindo a soberania, cidadania, dignidade da pessoa humana, valores sociais do trabalho e da livre iniciativa, 
            e pluralismo político.
            
            {f"**Análise do seu erro:** Você escolheu '{user_answer}', que não está correta porque esta alternativa contradiz o texto constitucional. É importante revisar os conceitos fundamentais para evitar confusões similares." if user_answer and user_answer != correct_answer else ""}
            
            **Dica para não errar:**
            Sempre lembre-se de que os fundamentos da República são diferentes dos objetivos fundamentais (Art. 3º). 
            Esta é uma pegadinha comum em concursos!
            
            **Estude mais:**
            Recomendo revisar os Arts. 1º a 4º da Constituição Federal, que tratam dos princípios fundamentais.
            """
        
        return Response({
            'explanation': explanation,
            'subject': subject,
            'generated_at': '2024-01-10T10:30:00Z'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao gerar explicação: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_study_recommendations(request):
    """
    Gera recomendações de estudo personalizadas baseadas no desempenho do usuário
    """
    try:
        user = request.user
        data = request.data
        
        # Dados de performance do usuário
        subject_performance = data.get('subject_performance', [])
        recent_mistakes = data.get('recent_mistakes', [])
        study_goals = data.get('study_goals', [])
        available_time = data.get('available_time_per_day', 60)  # em minutos
        
        # Simular análise de IA
        recommendations = generate_study_plan(
            subject_performance=subject_performance,
            recent_mistakes=recent_mistakes,
            study_goals=study_goals,
            available_time=available_time
        )
        
        return Response({
            'recommendations': recommendations,
            'generated_for': user.email,
            'generated_at': '2024-01-10T10:30:00Z'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao gerar recomendações: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_performance(request):
    """
    Análise inteligente do desempenho do usuário
    """
    try:
        data = request.data
        performance_data = data.get('performance_data', {})
        
        analysis = {
            'strengths': [],
            'weaknesses': [],
            'trends': [],
            'recommendations': [],
            'study_plan': {}
        }
        
        # Análise mock baseada em dados reais
        if performance_data:
            # Identificar pontos fortes
            best_subjects = sorted(
                performance_data.get('subjects', []),
                key=lambda x: x.get('accuracy', 0),
                reverse=True
            )[:3]
            
            analysis['strengths'] = [
                f"Excelente desempenho em {subject['name']} ({subject['accuracy']:.1f}%)"
                for subject in best_subjects if subject.get('accuracy', 0) > 80
            ]
            
            # Identificar pontos fracos
            weak_subjects = sorted(
                performance_data.get('subjects', []),
                key=lambda x: x.get('accuracy', 0)
            )[:3]
            
            analysis['weaknesses'] = [
                f"Precisa melhorar em {subject['name']} ({subject['accuracy']:.1f}%)"
                for subject in weak_subjects if subject.get('accuracy', 0) < 70
            ]
            
            # Tendências
            analysis['trends'] = [
                "Sua performance tem melhorado consistentemente nas últimas semanas",
                "Você está resolvendo questões mais rapidamente",
                "Tempo de estudo diário está dentro do recomendado"
            ]
            
            # Recomendações personalizadas
            analysis['recommendations'] = [
                "Foque 40% do tempo nas disciplinas com menor performance",
                "Continue praticando as disciplinas fortes para manter o nível",
                "Resolva pelo menos 20 questões por dia",
                "Revise os erros semanalmente"
            ]
            
            # Plano de estudos
            analysis['study_plan'] = {
                'daily_questions': 25,
                'review_frequency': 'weekly',
                'priority_subjects': [s['name'] for s in weak_subjects[:2]],
                'estimated_improvement_time': '4-6 semanas'
            }
        
        return Response(analysis)
        
    except Exception as e:
        return Response(
            {'error': f'Erro na análise: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_quiz_suggestions(request):
    """
    Sugere questões personalizadas baseadas no perfil do usuário
    """
    try:
        user = request.user
        data = request.data
        
        # Parâmetros da sugestão
        difficulty_preference = data.get('difficulty', 'adaptive')
        subject_focus = data.get('subject_focus', [])
        question_count = data.get('question_count', 10)
        time_available = data.get('time_available', 30)  # minutos
        
        # Lógica de sugestão (mock)
        suggestions = {
            'recommended_questions': [
                {
                    'id': i + 1,
                    'title': f'Questão Personalizada {i + 1}',
                    'subject': 'Direito Constitucional',
                    'difficulty': 'medium',
                    'estimated_time': 2,
                    'reason': 'Baseada em suas dificuldades recentes'
                }
                for i in range(question_count)
            ],
            'study_session': {
                'duration': f'{time_available} minutos',
                'focus_areas': subject_focus or ['Direito Constitucional', 'Direito Administrativo'],
                'success_probability': 75
            },
            'adaptive_settings': {
                'start_difficulty': 'medium',
                'adjust_based_on_performance': True,
                'explanation_detail_level': 'detailed'
            }
        }
        
        return Response(suggestions)
        
    except Exception as e:
        return Response(
            {'error': f'Erro ao gerar sugestões: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def generate_study_plan(subject_performance: List[Dict], recent_mistakes: List[Dict], 
                       study_goals: List[str], available_time: int) -> List[Dict]:
    """
    Gera plano de estudos personalizado
    """
    recommendations = []
    
    # Análise de performance por matéria
    if subject_performance:
        weak_subjects = [s for s in subject_performance if s.get('accuracy', 0) < 70]
        strong_subjects = [s for s in subject_performance if s.get('accuracy', 0) > 85]
        
        if weak_subjects:
            recommendations.append({
                'type': 'focus_subjects',
                'title': 'Foque nas disciplinas com menor performance',
                'description': f'Dedique 60% do tempo para: {", ".join([s["name"] for s in weak_subjects[:3]])}',
                'priority': 'high',
                'estimated_time': int(available_time * 0.6)
            })
        
        if strong_subjects:
            recommendations.append({
                'type': 'maintain_level',
                'title': 'Mantenha o nível das disciplinas fortes',
                'description': f'Continue praticando: {", ".join([s["name"] for s in strong_subjects[:2]])}',
                'priority': 'medium',
                'estimated_time': int(available_time * 0.3)
            })
    
    # Análise de erros recentes
    if recent_mistakes:
        common_topics = {}
        for mistake in recent_mistakes:
            topic = mistake.get('topic', 'Geral')
            common_topics[topic] = common_topics.get(topic, 0) + 1
        
        most_common = max(common_topics.items(), key=lambda x: x[1]) if common_topics else None
        if most_common:
            recommendations.append({
                'type': 'review_mistakes',
                'title': f'Revise: {most_common[0]}',
                'description': f'Você errou {most_common[1]} questões neste tópico recentemente',
                'priority': 'high',
                'estimated_time': 20
            })
    
    # Recomendações gerais
    recommendations.extend([
        {
            'type': 'daily_practice',
            'title': 'Prática diária',
            'description': f'Resolva {max(10, available_time // 3)} questões por dia',
            'priority': 'medium',
            'estimated_time': available_time // 2
        },
        {
            'type': 'weekly_review',
            'title': 'Revisão semanal',
            'description': 'Revise todas as questões erradas da semana',
            'priority': 'medium',
            'estimated_time': 60
        }
    ])
    
    return recommendations

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_tutor(request):
    """
    Chat inteligente com tutor virtual
    """
    try:
        data = request.data
        user_message = data.get('message', '')
        context = data.get('context', {})  # Contexto da conversa/questão
        
        if not user_message:
            return Response(
                {'error': 'Mensagem é obrigatória'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Resposta mock do tutor
        tutor_response = generate_tutor_response(user_message, context)
        
        return Response({
            'response': tutor_response,
            'timestamp': '2024-01-10T10:30:00Z',
            'tutor_id': 'ai_tutor_v1'
        })
        
    except Exception as e:
        return Response(
            {'error': f'Erro no chat: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def generate_tutor_response(message: str, context: Dict[str, Any]) -> str:
    """
    Gera resposta do tutor baseada na mensagem e contexto
    """
    message_lower = message.lower()
    
    # Respostas baseadas em padrões
    if 'não entendi' in message_lower or 'não compreendi' in message_lower:
        return """
        Entendo sua dúvida! Vou explicar de forma mais simples:
        
        Vamos quebrar o conceito em partes menores. Que parte específica está causando confusão? 
        Posso dar exemplos práticos ou usar analogias para facilitar o entendimento.
        
        💡 **Dica:** Tente identificar as palavras-chave da questão primeiro.
        """
    
    elif 'dica' in message_lower or 'ajuda' in message_lower:
        return """
        Aqui estão algumas dicas valiosas:
        
        📚 **Para questões de Direito:**
        • Leia com atenção as palavras "sempre", "nunca", "jamais" - geralmente indicam alternativas incorretas
        • Foque na literalidade da lei quando for texto constitucional
        • Cuidado com pegadinhas sobre competências (União, Estados, Municípios)
        
        ⏰ **Para gerenciar tempo:**
        • Não gaste mais de 2 minutos por questão
        • Marque questões difíceis para revisar depois
        • Comece pelas matérias que tem mais facilidade
        
        🎯 **Estratégia:**
        • Elimine alternativas obviamente erradas primeiro
        • Use seus conhecimentos prévios como âncora
        • Na dúvida entre duas, vá com a mais conservadora
        """
    
    elif 'motivação' in message_lower or 'desanimado' in message_lower:
        return """
        Eu entendo que estudar para concurso pode ser desafiador! 🌟
        
        Lembre-se:
        • Cada questão resolvida é um passo mais próximo da aprovação
        • Erros são oportunidades de aprendizado, não fracassos
        • Sua dedicação já mostra que você tem o que é necessário
        
        💪 **Estratégias para manter o foco:**
        • Defina metas pequenas e comemore cada conquista
        • Varie o tipo de estudo (questões, teoria, simulados)
        • Lembre-se do seu "por quê" - sua motivação inicial
        
        Continue firme! Estou aqui para ajudar sempre que precisar.
        """
    
    elif context.get('question_id'):
        return f"""
        Sobre esta questão específica:
        
        Esta é uma questão de {context.get('subject', 'concurso público')} que testa seu conhecimento sobre conceitos fundamentais.
        
        📝 **Abordagem recomendada:**
        1. Identifique o tema central da questão
        2. Relembre os conceitos-chave deste assunto
        3. Analise cada alternativa cuidadosamente
        4. Elimine as que claramente contradizem a teoria
        
        Precisa de esclarecimento sobre algum conceito específico?
        """
    
    else:
        return """
        Olá! Sou seu tutor virtual e estou aqui para ajudar! 📚
        
        Posso ajudá-lo com:
        • Explicações sobre questões específicas
        • Dicas de estudo e estratégias
        • Esclarecimento de conceitos jurídicos
        • Motivação e orientação nos estudos
        • Sugestões de plano de estudos personalizado
        
        Como posso ajudá-lo hoje? Seja específico para que eu possa dar a melhor orientação!
        """
    
    return response
