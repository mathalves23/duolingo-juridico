"""
Modelos centrais do sistema
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Subject(models.Model):
    """Matérias/Disciplinas"""
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Matéria'
        verbose_name_plural = 'Matérias'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Tags para categorização"""
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Cor em hex
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Article(models.Model):
    """Artigos/Conteúdo educativo"""
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=300, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    subjects = models.ManyToManyField(Subject, related_name='articles')
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles')
    is_published = models.BooleanField(default=False)
    featured_image = models.URLField(blank=True)
    reading_time = models.PositiveIntegerField(default=5)  # em minutos
    views_count = models.PositiveIntegerField(default=0)
    likes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Artigo'
        verbose_name_plural = 'Artigos'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Question(models.Model):
    """Questões/Perguntas"""
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Fácil'),
        ('medium', 'Médio'),
        ('hard', 'Difícil'),
    ]
    
    text = models.TextField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions')
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    explanation = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='questions')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_questions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Questão'
        verbose_name_plural = 'Questões'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Questão {self.id} - {self.subject.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    xp = models.IntegerField(default=0)
    coins = models.IntegerField(default=100)
    streak = models.IntegerField(default=0)
    last_activity = models.DateTimeField(default=timezone.now)
    level = models.IntegerField(default=1)
    subscription_type = models.CharField(max_length=20, default='free')
    subscription_expires = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Level {self.level}"
    
    @property
    def is_premium(self):
        return self.subscription_type in ['basic', 'premium', 'plus'] and \
               self.subscription_expires and self.subscription_expires > timezone.now()


class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_activities')
    activity_type = models.CharField(max_length=50, choices=[
        ('question_answered', 'Questão Respondida'),
        ('quiz_completed', 'Simulado Concluído'),
        ('achievement_earned', 'Conquista Obtida'),
        ('streak_milestone', 'Marco de Sequência'),
        ('level_up', 'Subiu de Nível'),
    ])
    description = models.CharField(max_length=255)
    points_earned = models.IntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'

    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"


class SubscriptionPlan(models.Model):
    PLAN_TYPES = [
        ('basic', 'Básico'),
        ('premium', 'Premium'),
        ('premium_plus', 'Premium Plus'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nome do Plano')
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, unique=True)
    description = models.TextField(verbose_name='Descrição')
    price_monthly = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Preço Mensal')
    price_yearly = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Preço Anual')
    features = models.JSONField(default=list, verbose_name='Recursos')
    max_questions_per_day = models.IntegerField(default=50, verbose_name='Questões por Dia')
    max_quizzes_per_day = models.IntegerField(default=5, verbose_name='Simulados por Dia')
    ai_explanations = models.BooleanField(default=False, verbose_name='Explicações IA')
    advanced_analytics = models.BooleanField(default=False, verbose_name='Analytics Avançado')
    priority_support = models.BooleanField(default=False, verbose_name='Suporte Prioritário')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plano de Assinatura'
        verbose_name_plural = 'Planos de Assinatura'
        ordering = ['price_monthly']

    def __str__(self):
        return f"{self.name} - R$ {self.price_monthly}/mês"


class Payment(models.Model):
    PAYMENT_METHODS = [
        ('pix', 'PIX'),
        ('credit_card', 'Cartão de Crédito'),
        ('debit_card', 'Cartão de Débito'),
        ('boleto', 'Boleto Bancário'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pendente'),
        ('processing', 'Processando'),
        ('completed', 'Concluído'),
        ('failed', 'Falhou'),
        ('cancelled', 'Cancelado'),
        ('refunded', 'Reembolsado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_payments')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Valor')
    currency = models.CharField(max_length=3, default='BRL', verbose_name='Moeda')
    billing_period = models.CharField(max_length=10, choices=[('monthly', 'Mensal'), ('yearly', 'Anual')])
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pagamento'
        verbose_name_plural = 'Pagamentos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Pagamento {self.user.username} - {self.subscription_plan.name} - {self.status}"


class Subscription(models.Model):
    SUBSCRIPTION_STATUS = [
        ('active', 'Ativa'),
        ('cancelled', 'Cancelada'),
        ('expired', 'Expirada'),
        ('suspended', 'Suspensa'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_subscription')
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default='active')
    billing_period = models.CharField(max_length=10, choices=[('monthly', 'Mensal'), ('yearly', 'Anual')])
    current_period_start = models.DateTimeField(verbose_name='Início do Período')
    current_period_end = models.DateTimeField(verbose_name='Fim do Período')
    cancel_at_period_end = models.BooleanField(default=False, verbose_name='Cancelar no Fim do Período')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    trial_end = models.DateTimeField(null=True, blank=True, verbose_name='Fim do Trial')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Assinatura'
        verbose_name_plural = 'Assinaturas'

    def __str__(self):
        return f"Assinatura {self.user.username} - {self.subscription_plan.name} - {self.status}"
        
    def is_active(self):
        from django.utils import timezone
        return (self.status == 'active' and 
                self.current_period_end > timezone.now())
    
    def days_remaining(self):
        from django.utils import timezone
        if self.current_period_end > timezone.now():
            return (self.current_period_end - timezone.now()).days
        return 0


class NotificationPreference(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True, verbose_name='Notificações por Email')
    push_notifications = models.BooleanField(default=True, verbose_name='Notificações Push')
    streak_reminders = models.BooleanField(default=True, verbose_name='Lembretes de Sequência')
    achievement_notifications = models.BooleanField(default=True, verbose_name='Notificações de Conquistas')
    social_notifications = models.BooleanField(default=True, verbose_name='Notificações Sociais')
    marketing_notifications = models.BooleanField(default=False, verbose_name='Notificações de Marketing')
    reminder_time = models.TimeField(default='19:00:00', verbose_name='Horário de Lembrete')
    reminder_days = models.JSONField(default=list, verbose_name='Dias de Lembrete')  # ['monday', 'tuesday', ...]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Preferência de Notificação'
        verbose_name_plural = 'Preferências de Notificações'

    def __str__(self):
        return f"Preferências de {self.user.username}"