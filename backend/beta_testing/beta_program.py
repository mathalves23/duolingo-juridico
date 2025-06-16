"""
Sistema de Testes Beta com Instituições Parceiras
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.db import models
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
import json
import logging
from celery import shared_task

User = get_user_model()
logger = logging.getLogger(__name__)


class BetaProgram(models.Model):
    """Programa de testes beta"""
    
    PROGRAM_TYPES = [
        ('institutional', 'Institucional'),
        ('individual', 'Individual'),
        ('instructor', 'Instrutor'),
        ('enterprise', 'Empresarial'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planejamento'),
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('completed', 'Concluído'),
        ('cancelled', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome do Programa")
    description = models.TextField(verbose_name="Descrição")
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES, verbose_name="Tipo")
    
    # Datas
    start_date = models.DateTimeField(verbose_name="Data de Início")
    end_date = models.DateTimeField(verbose_name="Data de Término")
    registration_deadline = models.DateTimeField(verbose_name="Prazo de Inscrição")
    
    # Limites
    max_participants = models.PositiveIntegerField(default=100, verbose_name="Máximo de Participantes")
    min_usage_hours = models.PositiveIntegerField(default=10, verbose_name="Horas Mínimas de Uso")
    
    # Features testadas
    features_to_test = models.JSONField(default=list, verbose_name="Features para Testar")
    feedback_requirements = models.JSONField(default=list, verbose_name="Requisitos de Feedback")
    
    # Incentivos
    rewards = models.JSONField(default=dict, verbose_name="Recompensas")
    certificates_enabled = models.BooleanField(default=True, verbose_name="Certificados Habilitados")
    
    # Status e coordenação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    coordinator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Coordenador")
    
    # Métricas
    total_feedback_received = models.PositiveIntegerField(default=0)
    average_satisfaction = models.FloatField(default=0.0)
    total_usage_hours = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Programa Beta'
        verbose_name_plural = 'Programas Beta'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"
    
    @property
    def is_active(self):
        now = timezone.now()
        return self.status == 'active' and self.start_date <= now <= self.end_date
    
    @property
    def days_remaining(self):
        if self.end_date > timezone.now():
            return (self.end_date - timezone.now()).days
        return 0
    
    def can_register(self):
        return (
            self.status == 'active' and
            timezone.now() < self.registration_deadline and
            self.participants.count() < self.max_participants
        )


class BetaParticipant(models.Model):
    """Participante do programa beta"""
    
    PARTICIPANT_TYPES = [
        ('student', 'Estudante'),
        ('instructor', 'Instrutor'),
        ('admin', 'Administrador'),
        ('tester', 'Testador Especializado'),
    ]
    
    STATUS_CHOICES = [
        ('registered', 'Registrado'),
        ('active', 'Ativo'),
        ('inactive', 'Inativo'),
        ('completed', 'Concluído'),
        ('dropped_out', 'Desistente'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(BetaProgram, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Tipo e status
    participant_type = models.CharField(max_length=20, choices=PARTICIPANT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered')
    
    # Dados de participação
    registration_date = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    total_usage_time = models.FloatField(default=0.0)  # em horas
    
    # Instituição (se aplicável)
    institution_name = models.CharField(max_length=200, blank=True)
    institution_role = models.CharField(max_length=100, blank=True)
    
    # Expectativas e objetivos
    testing_goals = models.TextField(blank=True, verbose_name="Objetivos de Teste")
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Iniciante'),
            ('intermediate', 'Intermediário'),
            ('advanced', 'Avançado'),
            ('expert', 'Especialista'),
        ],
        default='intermediate'
    )
    
    # Métricas de engajamento
    feedback_submissions = models.PositiveIntegerField(default=0)
    features_tested = models.JSONField(default=list)
    satisfaction_scores = models.JSONField(default=list)
    
    # Recompensas recebidas
    rewards_earned = models.JSONField(default=list)
    certificate_issued = models.BooleanField(default=False)
    certificate_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Participante Beta'
        verbose_name_plural = 'Participantes Beta'
        unique_together = ['program', 'user']
        ordering = ['-registration_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.program.name}"
    
    @property
    def completion_percentage(self):
        if not self.program.features_to_test:
            return 0
        
        tested_count = len(self.features_tested)
        total_count = len(self.program.features_to_test)
        return (tested_count / total_count) * 100 if total_count > 0 else 0
    
    @property
    def is_eligible_for_certificate(self):
        return (
            self.total_usage_time >= self.program.min_usage_hours and
            self.feedback_submissions >= 3 and
            self.completion_percentage >= 80
        )


class BetaFeedback(models.Model):
    """Feedback dos testes beta"""
    
    FEEDBACK_TYPES = [
        ('bug_report', 'Relatório de Bug'),
        ('feature_request', 'Solicitação de Feature'),
        ('usability', 'Usabilidade'),
        ('performance', 'Performance'),
        ('content_quality', 'Qualidade do Conteúdo'),
        ('general', 'Geral'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('critical', 'Crítica'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'Novo'),
        ('reviewing', 'Em Análise'),
        ('in_progress', 'Em Desenvolvimento'),
        ('resolved', 'Resolvido'),
        ('closed', 'Fechado'),
        ('wont_fix', 'Não Será Corrigido'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participant = models.ForeignKey(BetaParticipant, on_delete=models.CASCADE, related_name='feedbacks')
    
    # Tipo e classificação
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    
    # Conteúdo do feedback
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    feature_tested = models.CharField(max_length=100, blank=True, verbose_name="Feature Testada")
    
    # Reprodução (para bugs)
    steps_to_reproduce = models.TextField(blank=True, verbose_name="Passos para Reproduzir")
    expected_behavior = models.TextField(blank=True, verbose_name="Comportamento Esperado")
    actual_behavior = models.TextField(blank=True, verbose_name="Comportamento Atual")
    
    # Avaliações
    satisfaction_score = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Nota de Satisfação (1-5)"
    )
    ease_of_use = models.PositiveIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        verbose_name="Facilidade de Uso (1-5)"
    )
    
    # Informações técnicas
    browser_info = models.JSONField(default=dict, verbose_name="Informações do Navegador")
    device_info = models.JSONField(default=dict, verbose_name="Informações do Dispositivo")
    screenshots = models.JSONField(default=list, verbose_name="Screenshots")
    
    # Status e acompanhamento
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_beta_feedback'
    )
    
    # Resolução
    resolution_notes = models.TextField(blank=True, verbose_name="Notas de Resolução")
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Feedback Beta'
        verbose_name_plural = 'Feedbacks Beta'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.participant.user.get_full_name()}"


class InstitutionalPartner(models.Model):
    """Parceiro institucional para testes beta"""
    
    PARTNER_TYPES = [
        ('university', 'Universidade'),
        ('law_school', 'Faculdade de Direito'),
        ('prep_course', 'Curso Preparatório'),
        ('bar_association', 'OAB'),
        ('tribunal', 'Tribunal'),
        ('government', 'Órgão Governamental'),
    ]
    
    STATUS_CHOICES = [
        ('prospect', 'Prospecto'),
        ('negotiating', 'Negociando'),
        ('active', 'Ativo'),
        ('paused', 'Pausado'),
        ('ended', 'Finalizado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="Nome da Instituição")
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES)
    
    # Informações de contato
    contact_person = models.CharField(max_length=100, verbose_name="Pessoa de Contato")
    contact_email = models.EmailField(verbose_name="Email de Contato")
    contact_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefone")
    
    # Localização
    city = models.CharField(max_length=100, verbose_name="Cidade")
    state = models.CharField(max_length=2, verbose_name="Estado")
    region = models.CharField(max_length=20, verbose_name="Região")
    
    # Detalhes da parceria
    student_count = models.PositiveIntegerField(verbose_name="Número de Estudantes")
    instructor_count = models.PositiveIntegerField(verbose_name="Número de Instrutores")
    partnership_start = models.DateField(null=True, blank=True)
    partnership_end = models.DateField(null=True, blank=True)
    
    # Configurações específicas
    custom_features = models.JSONField(default=list, verbose_name="Features Customizadas")
    branding_options = models.JSONField(default=dict, verbose_name="Opções de Marca")
    integration_requirements = models.JSONField(default=dict, verbose_name="Requisitos de Integração")
    
    # Status e métricas
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='prospect')
    satisfaction_score = models.FloatField(default=0.0, verbose_name="Nota de Satisfação")
    total_usage_hours = models.FloatField(default=0.0, verbose_name="Total de Horas de Uso")
    
    # Responsável interno
    account_manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='managed_partners'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Parceiro Institucional'
        verbose_name_plural = 'Parceiros Institucionais'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_partner_type_display()})"
    
    @property
    def active_participants(self):
        return BetaParticipant.objects.filter(
            institution_name=self.name,
            status='active'
        ).count()


class BetaMetrics(models.Model):
    """Métricas do programa beta"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    program = models.ForeignKey(BetaProgram, on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField(verbose_name="Data")
    
    # Métricas de participação
    active_participants = models.PositiveIntegerField(default=0)
    new_registrations = models.PositiveIntegerField(default=0)
    dropouts = models.PositiveIntegerField(default=0)
    
    # Métricas de uso
    total_session_time = models.FloatField(default=0.0)  # em horas
    average_session_duration = models.FloatField(default=0.0)  # em minutos
    features_usage = models.JSONField(default=dict)
    
    # Métricas de feedback
    feedback_submissions = models.PositiveIntegerField(default=0)
    bugs_reported = models.PositiveIntegerField(default=0)
    feature_requests = models.PositiveIntegerField(default=0)
    average_satisfaction = models.FloatField(default=0.0)
    
    # Métricas de performance
    system_uptime = models.FloatField(default=100.0)  # percentual
    average_response_time = models.FloatField(default=0.0)  # em ms
    error_rate = models.FloatField(default=0.0)  # percentual
    
    class Meta:
        verbose_name = 'Métrica Beta'
        verbose_name_plural = 'Métricas Beta'
        unique_together = ['program', 'date']
        ordering = ['-date']


# Serviços para gestão do programa beta
class BetaProgramService:
    """Serviços para gestão do programa beta"""
    
    @staticmethod
    def register_participant(program_id: str, user_id: int, participant_data: Dict) -> Dict:
        """Registrar participante no programa beta"""
        try:
            program = BetaProgram.objects.get(id=program_id)
            user = User.objects.get(id=user_id)
            
            if not program.can_register():
                return {
                    'success': False,
                    'error': 'Programa não está aceitando registros'
                }
            
            # Verificar se já está registrado
            if BetaParticipant.objects.filter(program=program, user=user).exists():
                return {
                    'success': False,
                    'error': 'Usuário já está registrado neste programa'
                }
            
            # Criar participante
            participant = BetaParticipant.objects.create(
                program=program,
                user=user,
                participant_type=participant_data.get('type', 'student'),
                institution_name=participant_data.get('institution', ''),
                institution_role=participant_data.get('role', ''),
                testing_goals=participant_data.get('goals', ''),
                experience_level=participant_data.get('experience', 'intermediate')
            )
            
            # Enviar email de boas-vindas
            BetaProgramService._send_welcome_email(participant)
            
            return {
                'success': True,
                'participant_id': str(participant.id),
                'message': 'Registro realizado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao registrar participante: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }
    
    @staticmethod
    def submit_feedback(participant_id: str, feedback_data: Dict) -> Dict:
        """Submeter feedback de teste"""
        try:
            participant = BetaParticipant.objects.get(id=participant_id)
            
            feedback = BetaFeedback.objects.create(
                participant=participant,
                feedback_type=feedback_data['type'],
                title=feedback_data['title'],
                description=feedback_data['description'],
                feature_tested=feedback_data.get('feature', ''),
                steps_to_reproduce=feedback_data.get('steps', ''),
                expected_behavior=feedback_data.get('expected', ''),
                actual_behavior=feedback_data.get('actual', ''),
                satisfaction_score=feedback_data.get('satisfaction', 3),
                ease_of_use=feedback_data.get('ease_of_use', 3),
                browser_info=feedback_data.get('browser', {}),
                device_info=feedback_data.get('device', {}),
                screenshots=feedback_data.get('screenshots', [])
            )
            
            # Atualizar métricas do participante
            participant.feedback_submissions += 1
            participant.save()
            
            # Notificar equipe de desenvolvimento
            BetaProgramService._notify_development_team(feedback)
            
            return {
                'success': True,
                'feedback_id': str(feedback.id),
                'message': 'Feedback enviado com sucesso'
            }
            
        except Exception as e:
            logger.error(f"Erro ao submeter feedback: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }
    
    @staticmethod
    def track_feature_usage(participant_id: str, feature_name: str, usage_time: float):
        """Rastrear uso de features"""
        try:
            participant = BetaParticipant.objects.get(id=participant_id)
            
            # Adicionar feature à lista de testadas
            if feature_name not in participant.features_tested:
                participant.features_tested.append(feature_name)
            
            # Atualizar tempo de uso
            participant.total_usage_time += usage_time / 3600  # converter para horas
            participant.last_activity = timezone.now()
            participant.save()
            
            # Verificar se é elegível para certificado
            if participant.is_eligible_for_certificate and not participant.certificate_issued:
                BetaProgramService._issue_certificate(participant)
                
        except Exception as e:
            logger.error(f"Erro ao rastrear uso de feature: {e}")
    
    @staticmethod
    def _send_welcome_email(participant: BetaParticipant):
        """Enviar email de boas-vindas"""
        try:
            context = {
                'participant': participant,
                'program': participant.program,
                'login_url': f"{settings.FRONTEND_URL}/login"
            }
            
            html_content = render_to_string('emails/beta_welcome.html', context)
            
            send_mail(
                subject=f'Bem-vindo ao {participant.program.name}!',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[participant.user.email],
                html_message=html_content
            )
            
        except Exception as e:
            logger.error(f"Erro ao enviar email de boas-vindas: {e}")
    
    @staticmethod
    def _notify_development_team(feedback: BetaFeedback):
        """Notificar equipe de desenvolvimento sobre feedback"""
        try:
            if feedback.priority in ['high', 'critical']:
                # Enviar notificação urgente
                context = {
                    'feedback': feedback,
                    'participant': feedback.participant,
                    'program': feedback.participant.program
                }
                
                html_content = render_to_string('emails/urgent_feedback.html', context)
                
                send_mail(
                    subject=f'[URGENTE] Feedback Beta: {feedback.title}',
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEVELOPMENT_TEAM_EMAIL],
                    html_message=html_content
                )
                
        except Exception as e:
            logger.error(f"Erro ao notificar equipe: {e}")
    
    @staticmethod
    def _issue_certificate(participant: BetaParticipant):
        """Emitir certificado de participação"""
        try:
            participant.certificate_issued = True
            participant.certificate_date = timezone.now()
            participant.save()
            
            # Adicionar recompensa
            if 'certificate' not in participant.rewards_earned:
                participant.rewards_earned.append('certificate')
                participant.save()
            
            # Enviar email com certificado
            context = {
                'participant': participant,
                'program': participant.program,
                'certificate_url': f"{settings.FRONTEND_URL}/certificate/{participant.id}"
            }
            
            html_content = render_to_string('emails/beta_certificate.html', context)
            
            send_mail(
                subject='Certificado de Participação no Programa Beta',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[participant.user.email],
                html_message=html_content
            )
            
        except Exception as e:
            logger.error(f"Erro ao emitir certificado: {e}")
    
    @staticmethod
    def generate_program_report(program_id: str) -> Dict:
        """Gerar relatório do programa beta"""
        try:
            program = BetaProgram.objects.get(id=program_id)
            participants = program.participants.all()
            feedbacks = BetaFeedback.objects.filter(participant__program=program)
            
            # Métricas gerais
            total_participants = participants.count()
            active_participants = participants.filter(status='active').count()
            completed_participants = participants.filter(status='completed').count()
            
            # Métricas de uso
            total_usage_hours = sum(p.total_usage_time for p in participants)
            avg_usage_per_participant = total_usage_hours / max(1, total_participants)
            
            # Métricas de feedback
            total_feedbacks = feedbacks.count()
            avg_satisfaction = feedbacks.aggregate(
                avg=models.Avg('satisfaction_score')
            )['avg'] or 0
            
            # Feedback por tipo
            feedback_by_type = {}
            for feedback_type, _ in BetaFeedback.FEEDBACK_TYPES:
                count = feedbacks.filter(feedback_type=feedback_type).count()
                feedback_by_type[feedback_type] = count
            
            # Features mais testadas
            all_features = []
            for p in participants:
                all_features.extend(p.features_tested)
            
            feature_usage = {}
            for feature in all_features:
                feature_usage[feature] = feature_usage.get(feature, 0) + 1
            
            return {
                'success': True,
                'program': {
                    'name': program.name,
                    'type': program.get_program_type_display(),
                    'status': program.get_status_display(),
                    'start_date': program.start_date.isoformat(),
                    'end_date': program.end_date.isoformat(),
                    'days_remaining': program.days_remaining
                },
                'participation': {
                    'total_participants': total_participants,
                    'active_participants': active_participants,
                    'completed_participants': completed_participants,
                    'completion_rate': (completed_participants / max(1, total_participants)) * 100
                },
                'usage': {
                    'total_hours': round(total_usage_hours, 2),
                    'average_per_participant': round(avg_usage_per_participant, 2),
                    'feature_usage': feature_usage
                },
                'feedback': {
                    'total_submissions': total_feedbacks,
                    'average_satisfaction': round(avg_satisfaction, 2),
                    'feedback_by_type': feedback_by_type
                },
                'generated_at': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao gerar relatório: {e}")
            return {
                'success': False,
                'error': 'Erro interno do servidor'
            }


# Tarefas assíncronas
@shared_task
def send_weekly_beta_report():
    """Enviar relatório semanal dos programas beta"""
    active_programs = BetaProgram.objects.filter(status='active')
    
    for program in active_programs:
        report = BetaProgramService.generate_program_report(str(program.id))
        
        if report['success']:
            # Enviar para coordenador
            context = {
                'program': program,
                'report': report
            }
            
            html_content = render_to_string('emails/weekly_beta_report.html', context)
            
            send_mail(
                subject=f'Relatório Semanal - {program.name}',
                message='',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[program.coordinator.email],
                html_message=html_content
            )


@shared_task
def collect_daily_beta_metrics():
    """Coletar métricas diárias dos programas beta"""
    today = timezone.now().date()
    active_programs = BetaProgram.objects.filter(status='active')
    
    for program in active_programs:
        participants = program.participants.filter(status='active')
        feedbacks = BetaFeedback.objects.filter(
            participant__program=program,
            created_at__date=today
        )
        
        # Calcular métricas
        metrics = BetaMetrics.objects.create(
            program=program,
            date=today,
            active_participants=participants.count(),
            new_registrations=program.participants.filter(
                registration_date__date=today
            ).count(),
            feedback_submissions=feedbacks.count(),
            bugs_reported=feedbacks.filter(feedback_type='bug_report').count(),
            feature_requests=feedbacks.filter(feedback_type='feature_request').count(),
            average_satisfaction=feedbacks.aggregate(
                avg=models.Avg('satisfaction_score')
            )['avg'] or 0
        )
        
        logger.info(f"Métricas coletadas para {program.name}: {metrics}")


@shared_task
def remind_inactive_participants():
    """Lembrar participantes inativos"""
    cutoff_date = timezone.now() - timedelta(days=7)
    
    inactive_participants = BetaParticipant.objects.filter(
        status='active',
        last_activity__lt=cutoff_date
    )
    
    for participant in inactive_participants:
        context = {
            'participant': participant,
            'program': participant.program,
            'login_url': f"{settings.FRONTEND_URL}/login"
        }
        
        html_content = render_to_string('emails/beta_reminder.html', context)
        
        send_mail(
            subject='Que saudades! Continue testando conosco',
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[participant.user.email],
            html_message=html_content
        ) 