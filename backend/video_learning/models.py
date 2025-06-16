"""
Sistema de Video Learning com IA
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal

User = get_user_model()


class VideoSeries(models.Model):
    """Série de vídeos sobre um tópico"""
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Iniciante'),
        ('intermediate', 'Intermediário'),
        ('advanced', 'Avançado'),
        ('expert', 'Especialista'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Rascunho'),
        ('published', 'Publicado'),
        ('archived', 'Arquivado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    thumbnail = models.ImageField(upload_to='video_series/thumbnails/', verbose_name="Thumbnail")
    
    # Categorização
    subject = models.ForeignKey('courses.Subject', on_delete=models.CASCADE, verbose_name="Matéria")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, verbose_name="Dificuldade")
    tags = models.JSONField(default=list, verbose_name="Tags")
    
    # Instrutor
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='taught_series', verbose_name="Instrutor")
    
    # Configurações
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name="Status")
    is_premium = models.BooleanField(default=False, verbose_name="Premium")
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="Preço")
    
    # Estatísticas
    total_duration = models.PositiveIntegerField(default=0, verbose_name="Duração total (segundos)")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Visualizações")
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, verbose_name="Avaliação")
    rating_count = models.PositiveIntegerField(default=0, verbose_name="Número de avaliações")
    
    # IA Features
    ai_generated_summary = models.TextField(blank=True, verbose_name="Resumo gerado por IA")
    ai_difficulty_score = models.FloatField(null=True, blank=True, verbose_name="Score de dificuldade IA")
    ai_completion_time = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tempo estimado IA (minutos)")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Série de Vídeos"
        verbose_name_plural = "Séries de Vídeos"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    @property
    def total_videos(self):
        return self.videos.count()
    
    @property
    def completion_rate(self):
        total_enrollments = self.enrollments.count()
        if total_enrollments == 0:
            return 0
        completed = self.enrollments.filter(status='completed').count()
        return (completed / total_enrollments) * 100


class Video(models.Model):
    """Vídeo individual"""
    
    PROCESSING_STATUS = [
        ('uploading', 'Enviando'),
        ('processing', 'Processando'),
        ('ready', 'Pronto'),
        ('error', 'Erro'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(VideoSeries, on_delete=models.CASCADE, related_name='videos', verbose_name="Série")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    # Arquivo de vídeo
    video_file = models.FileField(upload_to='videos/', verbose_name="Arquivo de vídeo")
    thumbnail = models.ImageField(upload_to='videos/thumbnails/', blank=True, verbose_name="Thumbnail")
    duration = models.PositiveIntegerField(default=0, verbose_name="Duração (segundos)")
    
    # Processamento
    processing_status = models.CharField(max_length=20, choices=PROCESSING_STATUS, default='uploading', verbose_name="Status de processamento")
    video_url = models.URLField(blank=True, verbose_name="URL do vídeo processado")
    
    # IA Features
    ai_transcript = models.TextField(blank=True, verbose_name="Transcrição IA")
    ai_summary = models.TextField(blank=True, verbose_name="Resumo IA")
    ai_key_points = models.JSONField(default=list, verbose_name="Pontos-chave IA")
    ai_questions = models.JSONField(default=list, verbose_name="Questões geradas IA")
    
    # Configurações
    is_preview = models.BooleanField(default=False, verbose_name="Preview gratuito")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Vídeo"
        verbose_name_plural = "Vídeos"
        ordering = ['series', 'order']
    
    def __str__(self):
        return f"{self.series.title} - {self.title}"


class VideoEnrollment(models.Model):
    """Inscrição do usuário em uma série"""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('completed', 'Concluído'),
        ('paused', 'Pausado'),
        ('cancelled', 'Cancelado'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_enrollments', verbose_name="Usuário")
    series = models.ForeignKey(VideoSeries, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Série")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status")
    progress_percentage = models.FloatField(default=0.0, verbose_name="Progresso (%)")
    
    # Estatísticas
    total_watch_time = models.PositiveIntegerField(default=0, verbose_name="Tempo total assistido (segundos)")
    last_watched_video = models.ForeignKey(Video, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Último vídeo assistido")
    
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Inscrito em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    
    class Meta:
        verbose_name = "Inscrição em Série"
        verbose_name_plural = "Inscrições em Séries"
        unique_together = ['user', 'series']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.series.title}"


class VideoProgress(models.Model):
    """Progresso do usuário em vídeos individuais"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_progress', verbose_name="Usuário")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='user_progress', verbose_name="Vídeo")
    
    # Progresso
    watch_time = models.PositiveIntegerField(default=0, verbose_name="Tempo assistido (segundos)")
    last_position = models.PositiveIntegerField(default=0, verbose_name="Última posição (segundos)")
    is_completed = models.BooleanField(default=False, verbose_name="Concluído")
    completion_percentage = models.FloatField(default=0.0, verbose_name="Porcentagem concluída")
    
    # Interações
    liked = models.BooleanField(default=False, verbose_name="Curtiu")
    bookmarked = models.BooleanField(default=False, verbose_name="Salvou")
    notes = models.TextField(blank=True, verbose_name="Anotações")
    
    first_watched = models.DateTimeField(auto_now_add=True, verbose_name="Primeira visualização")
    last_watched = models.DateTimeField(auto_now=True, verbose_name="Última visualização")
    
    class Meta:
        verbose_name = "Progresso em Vídeo"
        verbose_name_plural = "Progressos em Vídeos"
        unique_together = ['user', 'video']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.video.title}"


class VideoNote(models.Model):
    """Anotações em timestamps específicos"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_notes', verbose_name="Usuário")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='notes', verbose_name="Vídeo")
    
    timestamp = models.PositiveIntegerField(verbose_name="Timestamp (segundos)")
    note = models.TextField(verbose_name="Anotação")
    
    # IA Features
    ai_context = models.TextField(blank=True, verbose_name="Contexto IA")
    ai_related_concepts = models.JSONField(default=list, verbose_name="Conceitos relacionados IA")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Anotação em Vídeo"
        verbose_name_plural = "Anotações em Vídeos"
        ordering = ['video', 'timestamp']
    
    def __str__(self):
        return f"{self.video.title} - {self.timestamp}s"


class VideoQuiz(models.Model):
    """Quiz baseado no conteúdo do vídeo"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='quizzes', verbose_name="Vídeo")
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descrição")
    
    # Configurações
    is_required = models.BooleanField(default=False, verbose_name="Obrigatório")
    passing_score = models.PositiveIntegerField(default=70, verbose_name="Pontuação mínima (%)")
    
    # IA Features
    ai_generated = models.BooleanField(default=False, verbose_name="Gerado por IA")
    ai_difficulty_level = models.FloatField(null=True, blank=True, verbose_name="Nível de dificuldade IA")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    
    class Meta:
        verbose_name = "Quiz de Vídeo"
        verbose_name_plural = "Quizzes de Vídeos"
    
    def __str__(self):
        return f"Quiz: {self.video.title}"


class VideoQuizQuestion(models.Model):
    """Questão do quiz de vídeo"""
    
    QUESTION_TYPES = [
        ('multiple_choice', 'Múltipla Escolha'),
        ('true_false', 'Verdadeiro/Falso'),
        ('fill_blank', 'Preencher Lacuna'),
        ('short_answer', 'Resposta Curta'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    quiz = models.ForeignKey(VideoQuiz, on_delete=models.CASCADE, related_name='questions', verbose_name="Quiz")
    
    question_text = models.TextField(verbose_name="Texto da questão")
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, verbose_name="Tipo")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    
    # Timestamp relacionado no vídeo
    video_timestamp = models.PositiveIntegerField(null=True, blank=True, verbose_name="Timestamp no vídeo")
    
    # Configurações
    points = models.PositiveIntegerField(default=1, verbose_name="Pontos")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Questão de Quiz"
        verbose_name_plural = "Questões de Quiz"
        ordering = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"


class VideoQuizAnswer(models.Model):
    """Alternativa de resposta"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(VideoQuizQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name="Questão")
    
    answer_text = models.TextField(verbose_name="Texto da resposta")
    is_correct = models.BooleanField(default=False, verbose_name="Correta")
    explanation = models.TextField(blank=True, verbose_name="Explicação")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Resposta de Quiz"
        verbose_name_plural = "Respostas de Quiz"
    
    def __str__(self):
        return f"{self.question} - {self.answer_text[:50]}"


class VideoQuizAttempt(models.Model):
    """Tentativa do usuário no quiz"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_quiz_attempts', verbose_name="Usuário")
    quiz = models.ForeignKey(VideoQuiz, on_delete=models.CASCADE, related_name='attempts', verbose_name="Quiz")
    
    score = models.FloatField(default=0.0, verbose_name="Pontuação")
    max_score = models.FloatField(default=0.0, verbose_name="Pontuação máxima")
    percentage = models.FloatField(default=0.0, verbose_name="Porcentagem")
    
    passed = models.BooleanField(default=False, verbose_name="Aprovado")
    time_taken = models.PositiveIntegerField(null=True, blank=True, verbose_name="Tempo gasto (segundos)")
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name="Iniciado em")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Concluído em")
    
    class Meta:
        verbose_name = "Tentativa de Quiz"
        verbose_name_plural = "Tentativas de Quiz"
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.quiz.title} ({self.percentage:.1f}%)"


class VideoRecommendation(models.Model):
    """Recomendações de vídeo baseadas em IA"""
    
    RECOMMENDATION_TYPES = [
        ('based_on_progress', 'Baseado no Progresso'),
        ('similar_content', 'Conteúdo Similar'),
        ('difficulty_progression', 'Progressão de Dificuldade'),
        ('weakness_improvement', 'Melhoria de Fraquezas'),
        ('trending', 'Em Alta'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_recommendations', verbose_name="Usuário")
    video_series = models.ForeignKey(VideoSeries, on_delete=models.CASCADE, verbose_name="Série recomendada")
    
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES, verbose_name="Tipo de recomendação")
    confidence_score = models.FloatField(verbose_name="Score de confiança")
    reason = models.TextField(verbose_name="Motivo da recomendação")
    
    # Interação do usuário
    viewed = models.BooleanField(default=False, verbose_name="Visualizada")
    clicked = models.BooleanField(default=False, verbose_name="Clicada")
    enrolled = models.BooleanField(default=False, verbose_name="Inscrito")
    dismissed = models.BooleanField(default=False, verbose_name="Dispensada")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    expires_at = models.DateTimeField(verbose_name="Expira em")
    
    class Meta:
        verbose_name = "Recomendação de Vídeo"
        verbose_name_plural = "Recomendações de Vídeos"
        ordering = ['-confidence_score', '-created_at']
    
    def __str__(self):
        return f"Recomendação para {self.user.get_full_name()}: {self.video_series.title}"


class VideoAnalytics(models.Model):
    """Analytics detalhados de visualização"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_analytics', verbose_name="Usuário")
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='analytics', verbose_name="Vídeo")
    
    # Dados da sessão
    session_id = models.UUIDField(verbose_name="ID da sessão")
    watch_duration = models.PositiveIntegerField(verbose_name="Duração assistida (segundos)")
    
    # Eventos de interação
    play_events = models.JSONField(default=list, verbose_name="Eventos de play")
    pause_events = models.JSONField(default=list, verbose_name="Eventos de pause")
    seek_events = models.JSONField(default=list, verbose_name="Eventos de seek")
    
    # Contexto
    device_type = models.CharField(max_length=50, blank=True, verbose_name="Tipo de dispositivo")
    browser = models.CharField(max_length=100, blank=True, verbose_name="Navegador")
    connection_speed = models.CharField(max_length=20, blank=True, verbose_name="Velocidade de conexão")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Analytics de Vídeo"
        verbose_name_plural = "Analytics de Vídeos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Analytics: {self.user.get_full_name()} - {self.video.title}" 