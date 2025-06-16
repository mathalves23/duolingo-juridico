"""
Modelos do sistema de cursos do Duolingo Jurídico
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class Subject(models.Model):
    """Disciplinas (ex: Direito Constitucional, Português, etc.)"""
    
    SUBJECT_CATEGORIES = [
        ('law', 'Direito'),
        ('language', 'Língua Portuguesa'),
        ('math', 'Matemática e Raciocínio Lógico'),
        ('technology', 'Informática'),
        ('administration', 'Administração Pública'),
        ('general', 'Conhecimentos Gerais'),
        ('specific', 'Conhecimentos Específicos'),
    ]
    
    name = models.CharField(max_length=200, unique=True)
    category = models.CharField(max_length=20, choices=SUBJECT_CATEGORIES)
    description = models.TextField()
    icon = models.ImageField(upload_to='subjects/icons/', blank=True, null=True)
    color_hex = models.CharField(max_length=7, default='#4285F4')  # Cor para UI
    
    # Ordenação e visibilidade
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    
    # Metadados
    total_lessons = models.PositiveIntegerField(default=0)
    estimated_hours = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Disciplina'
        verbose_name_plural = 'Disciplinas'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def update_lesson_count(self):
        """Atualiza contador de lições"""
        self.total_lessons = self.topics.aggregate(
            total=models.Sum('lessons__id')
        )['total'] or 0
        self.save()


class Topic(models.Model):
    """Tópicos dentro de cada disciplina"""
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Hierarquia
    parent_topic = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        blank=True, 
        null=True, 
        related_name='subtopics'
    )
    
    # Ordenação
    order = models.PositiveIntegerField(default=0)
    
    # Configurações de acesso
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    requires_previous_completion = models.BooleanField(default=True)
    
    # Metadados
    total_lessons = models.PositiveIntegerField(default=0)
    estimated_minutes = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Tópico'
        verbose_name_plural = 'Tópicos'
        ordering = ['subject', 'order', 'name']
        unique_together = ['subject', 'name']
    
    def __str__(self):
        return f"{self.subject.name} - {self.name}"
    
    @property
    def full_path(self):
        """Caminho completo do tópico"""
        if self.parent_topic:
            return f"{self.parent_topic.full_path} > {self.name}"
        return self.name


class Lesson(models.Model):
    """Lições dentro de cada tópico"""
    
    LESSON_TYPES = [
        ('theory', 'Teoria'),
        ('practice', 'Prática'),
        ('review', 'Revisão'),
        ('test', 'Teste'),
        ('challenge', 'Desafio'),
    ]
    
    DIFFICULTY_LEVELS = [
        (1, 'Básico - Letra da Lei'),
        (2, 'Intermediário - Interpretação'),
        (3, 'Avançado - Doutrina'),
        (4, 'Expert - Questões de Concurso'),
        (5, 'Master - Jurisprudência e Casos'),
    ]
    
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Tipo e dificuldade
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPES)
    difficulty_level = models.IntegerField(
        choices=DIFFICULTY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Conteúdo
    content = models.TextField()  # Conteúdo principal da lição
    legal_references = models.JSONField(default=list)  # Referências legais
    
    # Ordenação e acesso
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    
    # Gamificação
    xp_reward = models.PositiveIntegerField(default=10)
    coin_reward = models.PositiveIntegerField(default=5)
    
    # Metadados
    estimated_minutes = models.PositiveIntegerField(default=5)
    completion_count = models.PositiveIntegerField(default=0)
    average_score = models.FloatField(default=0.0)
    
    # Controle de versão do conteúdo jurídico
    content_version = models.CharField(max_length=20, default='1.0')
    last_legal_update = models.DateTimeField(auto_now_add=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Lição'
        verbose_name_plural = 'Lições'
        ordering = ['topic', 'order', 'title']
        unique_together = ['topic', 'title']
    
    def __str__(self):
        return f"{self.topic} - {self.title}"
    
    def update_completion_stats(self):
        """Atualiza estatísticas de conclusão"""
        completions = self.user_lessons.filter(completed=True)
        self.completion_count = completions.count()
        
        if completions.exists():
            avg_score = completions.aggregate(
                avg=models.Avg('score')
            )['avg']
            self.average_score = round(avg_score or 0, 2)
        
        self.save()


class UserLesson(models.Model):
    """Progresso do usuário em cada lição"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_lessons')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='user_lessons')
    
    # Status da lição
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    
    # Performance
    score = models.FloatField(default=0.0)  # Pontuação de 0 a 100
    attempts = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0)  # em segundos
    
    # Gamificação
    xp_earned = models.PositiveIntegerField(default=0)
    coins_earned = models.PositiveIntegerField(default=0)
    
    # Revisão espaçada
    next_review_date = models.DateTimeField(blank=True, null=True)
    review_interval_days = models.PositiveIntegerField(default=1)
    ease_factor = models.FloatField(default=2.5)  # Algoritmo SM-2
    
    class Meta:
        verbose_name = 'Progresso da Lição'
        verbose_name_plural = 'Progressos das Lições'
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.user.username} - {self.lesson.title}"
    
    def mark_completed(self, score):
        """Marca lição como concluída"""
        self.completed = True
        self.completed_at = timezone.now()
        self.score = score
        self.attempts += 1
        
        # Calcular XP e moedas baseado na performance
        base_xp = self.lesson.xp_reward
        base_coins = self.lesson.coin_reward
        
        # Bônus por performance
        if score >= 90:
            multiplier = 1.5
        elif score >= 80:
            multiplier = 1.2
        elif score >= 70:
            multiplier = 1.0
        else:
            multiplier = 0.8
        
        self.xp_earned = int(base_xp * multiplier)
        self.coins_earned = int(base_coins * multiplier)
        
        # Calcular próxima revisão (algoritmo de repetição espaçada)
        self.calculate_next_review(score)
        
        self.save()
        
        # Adicionar XP ao usuário
        self.user.add_xp(self.xp_earned)
        self.user.coins += self.coins_earned
        self.user.update_streak()
        self.user.save()
    
    def calculate_next_review(self, score):
        """Calcula próxima data de revisão usando algoritmo SM-2"""
        if score >= 60:  # Passou
            if self.attempts == 1:
                self.review_interval_days = 1
            elif self.attempts == 2:
                self.review_interval_days = 6
            else:
                self.review_interval_days = int(
                    self.review_interval_days * self.ease_factor
                )
            
            # Ajustar ease factor baseado na performance
            self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - score/20) * (0.08 + (5 - score/20) * 0.02)))
        else:  # Reprovou
            self.review_interval_days = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
        
        self.next_review_date = timezone.now() + timezone.timedelta(days=self.review_interval_days)


class LegalContent(models.Model):
    """Conteúdo jurídico atualizado automaticamente"""
    
    CONTENT_TYPES = [
        ('law', 'Lei'),
        ('decree', 'Decreto'),
        ('regulation', 'Regulamento'),
        ('jurisprudence', 'Jurisprudência'),
        ('doctrine', 'Doutrina'),
        ('summary', 'Súmula'),
    ]
    
    title = models.CharField(max_length=300)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    
    # Identificação oficial
    official_number = models.CharField(max_length=100, blank=True)  # Ex: Lei 8.112/90
    publication_date = models.DateField(blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    
    # Conteúdo
    full_text = models.TextField()
    summary = models.TextField(blank=True)
    
    # Metadados
    source_url = models.URLField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name='legal_contents')
    
    # Controle de versão
    version = models.CharField(max_length=20, default='1.0')
    is_current = models.BooleanField(default=True)
    replaced_by = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='replaces'
    )
    
    # Atualização automática
    last_checked = models.DateTimeField(auto_now=True)
    auto_update = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Conteúdo Jurídico'
        verbose_name_plural = 'Conteúdos Jurídicos'
        ordering = ['-publication_date', 'title']
        indexes = [
            models.Index(fields=['content_type', 'is_current']),
            models.Index(fields=['official_number']),
        ]
    
    def __str__(self):
        return f"{self.get_content_type_display()}: {self.title}"


class StudyPath(models.Model):
    """Trilhas de estudo personalizadas"""
    
    name = models.CharField(max_length=200)
    description = models.TextField()
    target_exam = models.CharField(max_length=200)  # Ex: "Concurso TRF", "OAB"
    
    # Configuração
    subjects = models.ManyToManyField(Subject, through='StudyPathSubject')
    estimated_weeks = models.PositiveIntegerField()
    difficulty_level = models.IntegerField(
        choices=Lesson.DIFFICULTY_LEVELS,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Visibilidade
    is_public = models.BooleanField(default=True)
    is_premium = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='created_paths'
    )
    
    # Estatísticas
    enrollment_count = models.PositiveIntegerField(default=0)
    completion_rate = models.FloatField(default=0.0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Trilha de Estudo'
        verbose_name_plural = 'Trilhas de Estudo'
        ordering = ['-enrollment_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.target_exam})"


class StudyPathSubject(models.Model):
    """Disciplinas em uma trilha de estudo"""
    
    study_path = models.ForeignKey(StudyPath, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    order = models.PositiveIntegerField(default=0)
    weight = models.FloatField(default=1.0)  # Peso da disciplina na trilha
    estimated_hours = models.PositiveIntegerField()
    
    class Meta:
        verbose_name = 'Disciplina da Trilha'
        verbose_name_plural = 'Disciplinas das Trilhas'
        unique_together = ['study_path', 'subject']
        ordering = ['order', 'subject__name']
    
    def __str__(self):
        return f"{self.study_path.name} - {self.subject.name}"


class UserStudyPath(models.Model):
    """Usuários matriculados em trilhas de estudo"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_paths')
    study_path = models.ForeignKey(StudyPath, on_delete=models.CASCADE, related_name='enrollments')
    
    enrolled_at = models.DateTimeField(auto_now_add=True)
    target_completion_date = models.DateField()
    
    # Progresso
    current_subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True
    )
    progress_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Matrícula em Trilha'
        verbose_name_plural = 'Matrículas em Trilhas'
        unique_together = ['user', 'study_path']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.study_path.name}"
    
    def update_progress(self):
        """Atualiza progresso na trilha"""
        # Calcular progresso baseado nas lições completadas
        total_lessons = 0
        completed_lessons = 0
        
        for path_subject in self.study_path.studypathsubject_set.all():
            subject_lessons = Lesson.objects.filter(
                topic__subject=path_subject.subject,
                is_active=True
            )
            total_lessons += subject_lessons.count()
            
            completed_lessons += UserLesson.objects.filter(
                user=self.user,
                lesson__in=subject_lessons,
                completed=True
            ).count()
        
        if total_lessons > 0:
            self.progress_percentage = (completed_lessons / total_lessons) * 100
            
            if self.progress_percentage >= 100:
                self.completed = True
                self.completed_at = timezone.now()
        
        self.save()
