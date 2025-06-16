"""
Modelos do serviço de IA do Duolingo Jurídico
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid
import json

User = get_user_model()


class AIModel(models.Model):
    """Modelos de IA utilizados no sistema"""
    
    MODEL_TYPES = [
        ('explanation', 'Explicação de Questões'),
        ('feedback', 'Feedback Personalizado'),
        ('content_generation', 'Geração de Conteúdo'),
        ('adaptive_learning', 'Aprendizado Adaptativo'),
        ('content_validation', 'Validação de Conteúdo'),
        ('question_difficulty', 'Classificação de Dificuldade'),
    ]
    
    PROVIDERS = [
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('google', 'Google AI'),
        ('local', 'Modelo Local'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=30, choices=MODEL_TYPES)
    provider = models.CharField(max_length=20, choices=PROVIDERS)
    
    # Configurações do modelo
    model_name = models.CharField(max_length=100)  # Ex: "gpt-4", "claude-3"
    api_endpoint = models.URLField(blank=True)
    
    # Configurações específicas
    max_tokens = models.PositiveIntegerField(default=1000)
    temperature = models.FloatField(default=0.7)
    system_prompt = models.TextField()
    
    # Configurações de uso
    cost_per_token = models.DecimalField(max_digits=10, decimal_places=8, default=0)
    rate_limit_per_minute = models.PositiveIntegerField(default=60)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Estatísticas
    total_requests = models.PositiveIntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Modelo de IA'
        verbose_name_plural = 'Modelos de IA'
        ordering = ['model_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"


class AIRequest(models.Model):
    """Requisições feitas aos modelos de IA"""
    
    REQUEST_TYPES = [
        ('explanation', 'Explicação de Questão'),
        ('feedback', 'Feedback de Resposta'),
        ('content_generation', 'Geração de Conteúdo'),
        ('adaptive_quiz', 'Quiz Adaptativo'),
        ('study_suggestion', 'Sugestão de Estudo'),
        ('legal_update', 'Atualização Legal'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('rate_limited', 'Limite de Taxa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='ai_requests',
        blank=True,
        null=True
    )
    model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='requests')
    
    # Tipo e contexto
    request_type = models.CharField(max_length=30, choices=REQUEST_TYPES)
    context = models.JSONField(default=dict)  # Contexto da requisição
    
    # Input e Output
    input_text = models.TextField()
    output_text = models.TextField(blank=True)
    
    # Metadados da requisição
    tokens_used = models.PositiveIntegerField(default=0)
    response_time_ms = models.PositiveIntegerField(default=0)
    cost = models.DecimalField(max_digits=8, decimal_places=6, default=0)
    
    # Status e controle
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Qualidade e feedback
    quality_score = models.FloatField(blank=True, null=True)  # 0-100
    user_feedback = models.TextField(blank=True)
    is_helpful = models.BooleanField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Requisição de IA'
        verbose_name_plural = 'Requisições de IA'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'request_type']),
            models.Index(fields=['model', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_request_type_display()} - {self.status} ({self.created_at})"


class LearningProfile(models.Model):
    """Perfil de aprendizado do usuário para IA adaptativa"""
    
    LEARNING_STYLES = [
        ('visual', 'Visual'),
        ('auditory', 'Auditivo'),
        ('kinesthetic', 'Cinestésico'),
        ('reading', 'Leitura/Escrita'),
        ('mixed', 'Misto'),
    ]
    
    DIFFICULTY_PREFERENCES = [
        ('gradual', 'Progressão Gradual'),
        ('challenge', 'Desafio Constante'),
        ('adaptive', 'Adaptativo'),
        ('review_heavy', 'Foco em Revisão'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='learning_profile'
    )
    
    # Estilo de aprendizado
    learning_style = models.CharField(
        max_length=20, 
        choices=LEARNING_STYLES, 
        default='adaptive'
    )
    difficulty_preference = models.CharField(
        max_length=20, 
        choices=DIFFICULTY_PREFERENCES, 
        default='adaptive'
    )
    
    # Padrões de estudo
    optimal_session_length = models.PositiveIntegerField(default=30)  # minutos
    preferred_study_times = models.JSONField(default=list)  # horários preferidos
    break_frequency = models.PositiveIntegerField(default=15)  # minutos entre pausas
    
    # Performance histórica
    subject_strengths = models.JSONField(default=dict)  # {subject_id: strength_score}
    subject_weaknesses = models.JSONField(default=dict)  # {subject_id: weakness_areas}
    question_type_performance = models.JSONField(default=dict)  # Performance por tipo
    
    # Padrões de erro
    common_mistakes = models.JSONField(default=list)
    error_patterns = models.JSONField(default=dict)
    improvement_areas = models.JSONField(default=list)
    
    # Motivação e engajamento
    motivation_triggers = models.JSONField(default=list)
    preferred_rewards = models.JSONField(default=list)
    engagement_patterns = models.JSONField(default=dict)
    
    # Adaptação de conteúdo
    content_complexity_level = models.FloatField(default=3.0)  # 1-5
    explanation_detail_level = models.FloatField(default=3.0)  # 1-5
    example_preference = models.CharField(
        max_length=20,
        choices=[
            ('theoretical', 'Teórico'),
            ('practical', 'Prático'),
            ('mixed', 'Misto'),
        ],
        default='mixed'
    )
    
    # Atualização automática
    last_analysis = models.DateTimeField(blank=True, null=True)
    analysis_frequency_days = models.PositiveIntegerField(default=7)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil de Aprendizado'
        verbose_name_plural = 'Perfis de Aprendizado'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def needs_analysis_update(self):
        """Verifica se precisa atualizar análise"""
        if not self.last_analysis:
            return True
        
        days_since_last = (timezone.now() - self.last_analysis).days
        return days_since_last >= self.analysis_frequency_days
    
    def update_subject_performance(self, subject_id, performance_data):
        """Atualiza performance em uma disciplina"""
        if not self.subject_strengths:
            self.subject_strengths = {}
        if not self.subject_weaknesses:
            self.subject_weaknesses = {}
        
        # Atualizar dados de performance
        self.subject_strengths[str(subject_id)] = performance_data.get('strength_score', 0)
        self.subject_weaknesses[str(subject_id)] = performance_data.get('weak_areas', [])
        
        self.save()


class AdaptiveLearningSession(models.Model):
    """Sessões de aprendizado adaptativo"""
    
    SESSION_TYPES = [
        ('practice', 'Prática'),
        ('review', 'Revisão'),
        ('challenge', 'Desafio'),
        ('remedial', 'Reforço'),
        ('assessment', 'Avaliação'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='adaptive_sessions')
    
    # Configuração da sessão
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES)
    target_subject = models.ForeignKey(
        'courses.Subject', 
        on_delete=models.CASCADE, 
        related_name='adaptive_sessions'
    )
    target_difficulty = models.FloatField()  # Dificuldade alvo calculada pela IA
    
    # Algoritmos utilizados
    content_selection_algorithm = models.CharField(max_length=50, default='adaptive_difficulty')
    question_ordering_algorithm = models.CharField(max_length=50, default='spaced_repetition')
    
    # Configurações adaptativas
    initial_difficulty = models.FloatField()
    difficulty_adjustment_rate = models.FloatField(default=0.1)
    performance_threshold = models.FloatField(default=0.7)
    
    # Resultados da sessão
    questions_attempted = models.PositiveIntegerField(default=0)
    questions_correct = models.PositiveIntegerField(default=0)
    average_response_time = models.FloatField(default=0.0)
    final_difficulty = models.FloatField(blank=True, null=True)
    
    # Status
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    
    # Análise pós-sessão
    performance_analysis = models.JSONField(default=dict)
    recommendations = models.JSONField(default=list)
    next_session_suggestions = models.JSONField(default=dict)
    
    class Meta:
        verbose_name = 'Sessão de Aprendizado Adaptativo'
        verbose_name_plural = 'Sessões de Aprendizado Adaptativo'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} ({self.target_subject.name})"
    
    @property
    def accuracy_rate(self):
        """Taxa de acerto da sessão"""
        if self.questions_attempted == 0:
            return 0
        return (self.questions_correct / self.questions_attempted) * 100
    
    def complete_session(self):
        """Finaliza a sessão e gera análise"""
        if self.is_completed:
            return
        
        self.is_completed = True
        self.completed_at = timezone.now()
        
        # Calcular dificuldade final baseada na performance
        if self.accuracy_rate >= 80:
            self.final_difficulty = min(5.0, self.target_difficulty + 0.2)
        elif self.accuracy_rate >= 60:
            self.final_difficulty = self.target_difficulty
        else:
            self.final_difficulty = max(1.0, self.target_difficulty - 0.2)
        
        # Gerar análise de performance
        self._generate_performance_analysis()
        
        # Atualizar perfil de aprendizado
        self._update_learning_profile()
        
        self.save()
    
    def _generate_performance_analysis(self):
        """Gera análise detalhada da performance"""
        analysis = {
            'accuracy_rate': self.accuracy_rate,
            'improvement_areas': [],
            'strengths': [],
            'difficulty_progression': {
                'initial': self.initial_difficulty,
                'final': self.final_difficulty,
                'change': self.final_difficulty - self.initial_difficulty
            }
        }
        
        # Identificar áreas de melhoria
        if self.accuracy_rate < 70:
            analysis['improvement_areas'].append('Precisão geral')
        
        if self.average_response_time > 120:  # mais de 2 minutos por questão
            analysis['improvement_areas'].append('Velocidade de resposta')
        
        # Identificar pontos fortes
        if self.accuracy_rate >= 85:
            analysis['strengths'].append('Alta precisão')
        
        if self.average_response_time < 60:  # menos de 1 minuto por questão
            analysis['strengths'].append('Resposta rápida')
        
        self.performance_analysis = analysis
    
    def _update_learning_profile(self):
        """Atualiza o perfil de aprendizado baseado na sessão"""
        profile, created = LearningProfile.objects.get_or_create(user=self.user)
        
        # Atualizar performance da disciplina
        subject_id = str(self.target_subject.id)
        if not profile.subject_strengths:
            profile.subject_strengths = {}
        
        # Média ponderada com performance anterior
        current_performance = self.accuracy_rate / 100
        previous_performance = profile.subject_strengths.get(subject_id, 0.5)
        
        # Dar mais peso à performance recente
        new_performance = (0.3 * previous_performance) + (0.7 * current_performance)
        profile.subject_strengths[subject_id] = new_performance
        
        # Ajustar nível de complexidade de conteúdo
        if self.accuracy_rate >= 85:
            profile.content_complexity_level = min(5.0, profile.content_complexity_level + 0.1)
        elif self.accuracy_rate < 60:
            profile.content_complexity_level = max(1.0, profile.content_complexity_level - 0.2)
        
        profile.last_analysis = timezone.now()
        profile.save()


class AIFeedback(models.Model):
    """Feedback personalizado gerado pela IA"""
    
    FEEDBACK_TYPES = [
        ('answer_explanation', 'Explicação de Resposta'),
        ('study_suggestion', 'Sugestão de Estudo'),
        ('performance_analysis', 'Análise de Performance'),
        ('motivation', 'Motivacional'),
        ('correction', 'Correção'),
        ('encouragement', 'Encorajamento'),
    ]
    
    FEEDBACK_CONTEXTS = [
        ('question_wrong', 'Resposta Incorreta'),
        ('question_correct', 'Resposta Correta'),
        ('session_complete', 'Sessão Concluída'),
        ('streak_broken', 'Streak Quebrado'),
        ('achievement_unlocked', 'Conquista Desbloqueada'),
        ('difficulty_adjustment', 'Ajuste de Dificuldade'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_feedback')
    
    # Tipo e contexto
    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPES)
    context = models.CharField(max_length=30, choices=FEEDBACK_CONTEXTS)
    
    # Conteúdo relacionado
    question = models.ForeignKey(
        'questions.Question', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    user_answer = models.ForeignKey(
        'questions.UserAnswer', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    session = models.ForeignKey(
        AdaptiveLearningSession, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    
    # Conteúdo do feedback
    title = models.CharField(max_length=200)
    content = models.TextField()
    additional_resources = models.JSONField(default=list)  # Links, referências extras
    
    # Personalização
    user_learning_style = models.CharField(max_length=20, blank=True)
    difficulty_level = models.FloatField(default=3.0)
    tone = models.CharField(
        max_length=20,
        choices=[
            ('formal', 'Formal'),
            ('casual', 'Casual'),
            ('encouraging', 'Encorajador'),
            ('direct', 'Direto'),
        ],
        default='encouraging'
    )
    
    # Qualidade e efetividade
    ai_confidence = models.FloatField(default=0.0)  # Confiança da IA na resposta
    user_rating = models.PositiveIntegerField(blank=True, null=True)  # 1-5
    was_helpful = models.BooleanField(blank=True, null=True)
    user_feedback_text = models.TextField(blank=True)
    
    # Metadados
    ai_model_used = models.ForeignKey(
        AIModel, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    generation_time_ms = models.PositiveIntegerField(default=0)
    tokens_used = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Feedback de IA'
        verbose_name_plural = 'Feedbacks de IA'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'feedback_type']),
            models.Index(fields=['context', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_feedback_type_display()} - {self.user.username}"


class ContentValidation(models.Model):
    """Validação de conteúdo jurídico pela IA"""
    
    VALIDATION_TYPES = [
        ('legal_accuracy', 'Precisão Legal'),
        ('content_freshness', 'Atualidade do Conteúdo'),
        ('difficulty_assessment', 'Avaliação de Dificuldade'),
        ('quality_check', 'Verificação de Qualidade'),
        ('plagiarism_check', 'Verificação de Plágio'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('validated', 'Validado'),
        ('flagged', 'Sinalizado'),
        ('outdated', 'Desatualizado'),
        ('error', 'Erro na Validação'),
    ]
    
    # Conteúdo sendo validado
    question = models.ForeignKey(
        'questions.Question', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='validations'
    )
    lesson = models.ForeignKey(
        'courses.Lesson', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='validations'
    )
    legal_content = models.ForeignKey(
        'courses.LegalContent', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True,
        related_name='validations'
    )
    
    # Tipo de validação
    validation_type = models.CharField(max_length=30, choices=VALIDATION_TYPES)
    
    # Resultados da validação
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confidence_score = models.FloatField(default=0.0)  # 0-100
    
    # Detalhes da validação
    validation_details = models.JSONField(default=dict)
    issues_found = models.JSONField(default=list)
    suggestions = models.JSONField(default=list)
    
    # IA utilizada
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    
    # Timestamps
    validated_at = models.DateTimeField(auto_now_add=True)
    content_last_modified = models.DateTimeField()
    
    class Meta:
        verbose_name = 'Validação de Conteúdo'
        verbose_name_plural = 'Validações de Conteúdo'
        ordering = ['-validated_at']
    
    def __str__(self):
        content_type = 'Questão' if self.question else 'Lição' if self.lesson else 'Conteúdo Legal'
        return f"{self.get_validation_type_display()} - {content_type} ({self.status})"


class UserStudyRecommendation(models.Model):
    """Recomendações de estudo personalizadas pela IA"""
    
    RECOMMENDATION_TYPES = [
        ('next_lesson', 'Próxima Lição'),
        ('review_session', 'Sessão de Revisão'),
        ('practice_quiz', 'Quiz de Prática'),
        ('weak_area_focus', 'Foco em Área Fraca'),
        ('difficulty_adjustment', 'Ajuste de Dificuldade'),
        ('study_schedule', 'Cronograma de Estudos'),
    ]
    
    PRIORITIES = [
        ('low', 'Baixa'),
        ('medium', 'Média'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_recommendations')
    
    # Tipo e prioridade
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITIES, default='medium')
    
    # Conteúdo da recomendação
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField()  # Por que esta recomendação foi feita
    
    # Ação recomendada
    recommended_content = models.JSONField(default=dict)  # IDs de lições, questões, etc.
    estimated_time_minutes = models.PositiveIntegerField(default=30)
    optimal_timing = models.JSONField(default=dict)  # Melhor horário para estudar
    
    # Baseado em análise
    based_on_performance = models.JSONField(default=dict)
    learning_profile_factors = models.JSONField(default=dict)
    
    # Status e feedback
    is_active = models.BooleanField(default=True)
    was_followed = models.BooleanField(blank=True, null=True)
    user_feedback = models.TextField(blank=True)
    effectiveness_score = models.FloatField(blank=True, null=True)  # 0-100
    
    # IA utilizada
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE)
    confidence_score = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()  # Recomendação expira
    followed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Recomendação de Estudo'
        verbose_name_plural = 'Recomendações de Estudo'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['priority', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username} ({self.priority})"
    
    @property
    def is_expired(self):
        """Verifica se a recomendação expirou"""
        return timezone.now() > self.expires_at
    
    def mark_followed(self):
        """Marca recomendação como seguida"""
        self.was_followed = True
        self.followed_at = timezone.now()
        self.save()
