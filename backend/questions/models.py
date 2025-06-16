"""
Modelos do sistema de questões e simulados do Duolingo Jurídico
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class ExamBoard(models.Model):
    """Bancas examinadoras"""
    
    name = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='exam_boards/', blank=True, null=True)
    
    # Estatísticas
    total_questions = models.PositiveIntegerField(default=0)
    difficulty_average = models.FloatField(default=3.0)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Banca Examinadora'
        verbose_name_plural = 'Bancas Examinadoras'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.acronym} - {self.name}"


class Question(models.Model):
    """Questões de concursos"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Múltipla Escolha'),
        ('true_false', 'Verdadeiro ou Falso'),
        ('fill_blank', 'Preencher Lacunas'),
        ('order_items', 'Ordenar Itens'),
        ('match_pairs', 'Associar Pares'),
        ('essay', 'Dissertativa'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Muito Fácil'),
        (2, 'Fácil'),
        (3, 'Médio'),
        (4, 'Difícil'),
        (5, 'Muito Difícil'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=500)
    statement = models.TextField()  # Enunciado da questão
    
    # Tipo e dificuldade
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Relacionamentos
    subject = models.ForeignKey(
        'courses.Subject', 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    topic = models.ForeignKey(
        'courses.Topic', 
        on_delete=models.CASCADE, 
        related_name='questions',
        blank=True,
        null=True
    )
    exam_board = models.ForeignKey(
        ExamBoard, 
        on_delete=models.CASCADE, 
        related_name='questions'
    )
    
    # Informações da fonte
    exam_name = models.CharField(max_length=200)  # Ex: "TRF 2ª Região"
    exam_year = models.PositiveIntegerField()
    exam_date = models.DateField(blank=True, null=True)
    source_url = models.URLField(blank=True)
    
    # Conteúdo jurídico relacionado
    legal_references = models.JSONField(default=list)  # Referências legais
    related_jurisprudence = models.TextField(blank=True)
    doctrine_explanation = models.TextField(blank=True)
    
    # Metadados
    tags = models.JSONField(default=list)  # Tags para categorização
    estimated_time_seconds = models.PositiveIntegerField(default=60)
    
    # Estatísticas
    times_answered = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    average_time = models.FloatField(default=0.0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['-exam_year', 'exam_name']
        indexes = [
            models.Index(fields=['subject', 'difficulty_level']),
            models.Index(fields=['exam_board', 'exam_year']),
            models.Index(fields=['question_type', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.exam_board.acronym} {self.exam_year} - {self.title[:50]}..."
    
    @property
    def accuracy_rate(self):
        """Taxa de acerto da questão"""
        if self.times_answered == 0:
            return 0
        return round((self.correct_answers / self.times_answered) * 100, 2)
    
    def update_statistics(self):
        """Atualiza estatísticas da questão"""
        user_answers = self.user_answers.all()
        self.times_answered = user_answers.count()
        self.correct_answers = user_answers.filter(is_correct=True).count()
        
        if user_answers.exists():
            avg_time = user_answers.aggregate(
                avg=models.Avg('time_spent')
            )['avg']
            self.average_time = round(avg_time or 0, 2)
        
        self.save()


class QuestionOption(models.Model):
    """Alternativas de questões de múltipla escolha"""
    
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='options'
    )
    
    letter = models.CharField(max_length=1)  # A, B, C, D, E
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    
    # Para questões com explicações por alternativa
    explanation = models.TextField(blank=True)
    
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        verbose_name = 'Alternativa'
        verbose_name_plural = 'Alternativas'
        ordering = ['order', 'letter']
        unique_together = ['question', 'letter']
    
    def __str__(self):
        return f"{self.question.title[:30]}... - {self.letter}) {self.text[:50]}..."


class QuestionExplanation(models.Model):
    """Explicações detalhadas das questões"""
    
    question = models.OneToOneField(
        Question, 
        on_delete=models.CASCADE, 
        related_name='explanation'
    )
    
    # Explicação geral
    general_explanation = models.TextField()
    
    # Explicação por alternativa (para múltipla escolha)
    options_explanation = models.JSONField(default=dict)
    
    # Referências complementares
    legal_articles = models.JSONField(default=list)
    jurisprudence_references = models.TextField(blank=True)
    doctrine_citations = models.TextField(blank=True)
    
    # Dicas e estratégias
    solution_tips = models.TextField(blank=True)
    common_mistakes = models.TextField(blank=True)
    
    # IA Enhancement
    ai_generated = models.BooleanField(default=False)
    ai_confidence = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Explicação da Questão'
        verbose_name_plural = 'Explicações das Questões'
    
    def __str__(self):
        return f"Explicação: {self.question.title[:50]}..."


class UserAnswer(models.Model):
    """Respostas dos usuários às questões"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    
    # Resposta do usuário
    selected_option = models.ForeignKey(
        QuestionOption, 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True
    )
    text_answer = models.TextField(blank=True)  # Para questões dissertativas
    
    # Resultado
    is_correct = models.BooleanField()
    score = models.FloatField(default=0.0)  # Pontuação obtida
    
    # Métricas
    time_spent = models.PositiveIntegerField()  # em segundos
    attempts = models.PositiveIntegerField(default=1)
    
    # Contexto
    answered_in_lesson = models.ForeignKey(
        'courses.Lesson', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    answered_in_quiz = models.ForeignKey(
        'Quiz', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    
    # Feedback da IA
    ai_feedback = models.TextField(blank=True)
    feedback_requested = models.BooleanField(default=False)
    
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Resposta do Usuário'
        verbose_name_plural = 'Respostas dos Usuários'
        ordering = ['-answered_at']
        indexes = [
            models.Index(fields=['user', 'is_correct']),
            models.Index(fields=['question', 'answered_at']),
        ]
    
    def __str__(self):
        result = "✓" if self.is_correct else "✗"
        return f"{result} {self.user.username} - {self.question.title[:30]}..."


class Quiz(models.Model):
    """Simulados e quizzes"""
    
    QUIZ_TYPES = [
        ('lesson_quiz', 'Quiz da Lição'),
        ('topic_review', 'Revisão do Tópico'),
        ('subject_test', 'Teste da Disciplina'),
        ('mock_exam', 'Simulado Completo'),
        ('custom_quiz', 'Quiz Personalizado'),
        ('adaptive_quiz', 'Quiz Adaptativo (IA)'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]
    
    # Identificação
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Tipo e configuração
    quiz_type = models.CharField(max_length=20, choices=QUIZ_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Relacionamentos
    subjects = models.ManyToManyField('courses.Subject', related_name='quizzes')
    exam_board = models.ForeignKey(
        ExamBoard, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    
    # Configurações
    time_limit_minutes = models.PositiveIntegerField(blank=True, null=True)
    max_questions = models.PositiveIntegerField(default=20)
    difficulty_level = models.IntegerField(
        choices=Question.DIFFICULTY_LEVELS,
        blank=True,
        null=True
    )
    
    # Filtros de questões
    min_year = models.PositiveIntegerField(blank=True, null=True)
    max_year = models.PositiveIntegerField(blank=True, null=True)
    
    # Gamificação
    xp_reward = models.PositiveIntegerField(default=50)
    coin_reward = models.PositiveIntegerField(default=20)
    
    # Acesso
    is_premium = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    
    # Metadados
    total_attempts = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    average_time = models.FloatField(default=0.0)
    
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='created_quizzes'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Quiz/Simulado'
        verbose_name_plural = 'Quizzes/Simulados'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_quiz_type_display()}: {self.title}"
    
    def get_questions(self, user=None):
        """Retorna questões para o quiz"""
        questions = Question.objects.filter(
            subject__in=self.subjects.all(),
            is_active=True
        )
        
        # Aplicar filtros
        if self.exam_board:
            questions = questions.filter(exam_board=self.exam_board)
        
        if self.difficulty_level:
            questions = questions.filter(difficulty_level=self.difficulty_level)
        
        if self.min_year:
            questions = questions.filter(exam_year__gte=self.min_year)
        
        if self.max_year:
            questions = questions.filter(exam_year__lte=self.max_year)
        
        # Para quiz adaptativo, usar IA para selecionar questões
        if self.quiz_type == 'adaptive_quiz' and user:
            return self._get_adaptive_questions(user, questions)
        
        # Ordenação aleatória e limite
        return questions.order_by('?')[:self.max_questions]
    
    def _get_adaptive_questions(self, user, questions):
        """Seleciona questões adaptadas ao nível do usuário"""
        # Analisar histórico do usuário
        user_stats = user.user_answers.aggregate(
            avg_accuracy=models.Avg('score'),
            total_answers=models.Count('id')
        )
        
        accuracy = user_stats['avg_accuracy'] or 50
        
        # Ajustar dificuldade baseada na performance
        if accuracy >= 80:
            target_difficulty = min(5, user.current_level // 2 + 3)
        elif accuracy >= 60:
            target_difficulty = min(4, user.current_level // 2 + 2)
        else:
            target_difficulty = max(1, user.current_level // 2)
        
        # Focar em áreas fracas
        weak_subjects = user.profile.weak_subjects if hasattr(user, 'profile') else []
        if weak_subjects:
            questions = questions.filter(
                subject__name__in=weak_subjects
            ).union(
                questions.filter(difficulty_level=target_difficulty)
            )
        else:
            questions = questions.filter(difficulty_level=target_difficulty)
        
        return questions.order_by('?')[:self.max_questions]


class QuizAttempt(models.Model):
    """Tentativas de quizzes pelos usuários"""
    
    STATUS_CHOICES = [
        ('in_progress', 'Em Andamento'),
        ('completed', 'Concluído'),
        ('abandoned', 'Abandonado'),
        ('time_expired', 'Tempo Expirado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    
    # Status e timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    time_spent = models.PositiveIntegerField(default=0)  # em segundos
    
    # Resultados
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    score = models.FloatField(default=0.0)  # Pontuação final
    
    # Gamificação
    xp_earned = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    
    # Análise de performance
    subject_scores = models.JSONField(default=dict)  # Score por disciplina
    difficulty_breakdown = models.JSONField(default=dict)  # Performance por dificuldade
    
    class Meta:
        verbose_name = 'Tentativa de Quiz'
        verbose_name_plural = 'Tentativas de Quizzes'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['quiz', 'completed_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.quiz.title} ({self.score:.1f}%)"
    
    @property
    def accuracy_rate(self):
        """Taxa de acerto"""
        if self.total_questions == 0:
            return 0
        return round((self.correct_answers / self.total_questions) * 100, 2)
    
    def complete_attempt(self):
        """Finaliza a tentativa e calcula resultados"""
        if self.status != 'in_progress':
            return
        
        self.status = 'completed'
        self.completed_at = timezone.now()
        
        # Calcular tempo total
        self.time_spent = int((self.completed_at - self.started_at).total_seconds())
        
        # Calcular score final
        self.score = self.accuracy_rate
        
        # Calcular recompensas
        base_xp = self.quiz.xp_reward
        base_coins = self.quiz.coin_reward
        
        # Bônus por performance
        if self.score >= 90:
            multiplier = 1.5
        elif self.score >= 80:
            multiplier = 1.2
        elif self.score >= 70:
            multiplier = 1.0
        else:
            multiplier = 0.8
        
        self.xp_earned = int(base_xp * multiplier)
        self.coins_earned = int(base_coins * multiplier)
        
        self.save()
        
        # Atualizar usuário
        self.user.add_xp(self.xp_earned)
        self.user.coins += self.coins_earned
        self.user.update_streak()
        self.user.save()
        
        # Atualizar estatísticas do quiz
        self.quiz.total_attempts += 1
        self.quiz.save()


class QuestionReport(models.Model):
    """Denúncias de questões pelos usuários"""
    
    REPORT_TYPES = [
        ('incorrect_answer', 'Gabarito Incorreto'),
        ('outdated_law', 'Lei Desatualizada'),
        ('typo', 'Erro de Digitação'),
        ('unclear_statement', 'Enunciado Confuso'),
        ('duplicate', 'Questão Duplicada'),
        ('inappropriate', 'Conteúdo Inapropriado'),
        ('other', 'Outro'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('reviewing', 'Em Análise'),
        ('resolved', 'Resolvido'),
        ('rejected', 'Rejeitado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_reports')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reports')
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Resolução
    reviewed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='reviewed_reports'
    )
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Denúncia de Questão'
        verbose_name_plural = 'Denúncias de Questões'
        ordering = ['-created_at']
        unique_together = ['user', 'question', 'report_type']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.question.title[:30]}..."
