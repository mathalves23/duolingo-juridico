"""
Modelos do sistema de usuários do Duolingo Jurídico
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from cryptography.fernet import Fernet
from django.conf import settings
import json


class User(AbstractUser):
    """Modelo de usuário customizado"""
    
    SUBSCRIPTION_CHOICES = [
        ('free', 'Gratuito'),
        ('premium', 'Premium'),
        ('premium_plus', 'Premium Plus'),
    ]
    
    # Informações básicas
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Gamificação
    total_xp = models.PositiveIntegerField(default=0)
    current_level = models.PositiveIntegerField(default=1)
    coins = models.PositiveIntegerField(default=0)
    gems = models.PositiveIntegerField(default=5)  # Premium currency
    
    # Streak system
    current_streak = models.PositiveIntegerField(default=0)
    longest_streak = models.PositiveIntegerField(default=0)
    last_study_date = models.DateField(blank=True, null=True)
    
    # Subscription
    subscription_type = models.CharField(
        max_length=20, 
        choices=SUBSCRIPTION_CHOICES, 
        default='free'
    )
    subscription_expires = models.DateTimeField(blank=True, null=True)
    
    # Study preferences
    daily_goal = models.PositiveIntegerField(default=50)  # XP diário
    reminder_time = models.TimeField(blank=True, null=True)
    study_days = models.JSONField(default=list)  # [1,2,3,4,5] = segunda a sexta
    
    # Privacy and LGPD
    agreed_to_terms = models.BooleanField(default=False)
    agreed_to_lgpd = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)
    data_processing_consent = models.BooleanField(default=False)
    
    # Profile
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    target_exam = models.CharField(max_length=200, blank=True)
    
    # Analytics
    total_study_time = models.PositiveIntegerField(default=0)  # em minutos
    total_questions_answered = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    
    # Account status
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['-total_xp']
    
    # Resolver conflitos de reverse accessor
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_users',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_users',
        related_query_name='custom_user',
    )
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    @property
    def accuracy_rate(self):
        """Taxa de acerto do usuário"""
        if self.total_questions_answered == 0:
            return 0
        return round((self.correct_answers / self.total_questions_answered) * 100, 2)
    
    @property
    def is_premium(self):
        """Verifica se o usuário tem assinatura ativa"""
        if self.subscription_type == 'free':
            return False
        if self.subscription_expires and self.subscription_expires > timezone.now():
            return True
        return False
    
    def update_streak(self):
        """Atualiza sequência de estudos"""
        today = timezone.now().date()
        
        if not self.last_study_date:
            self.current_streak = 1
        elif self.last_study_date == today:
            # Já estudou hoje
            return
        elif self.last_study_date == today - timezone.timedelta(days=1):
            # Estudou ontem, mantém sequência
            self.current_streak += 1
        else:
            # Quebrou a sequência
            self.current_streak = 1
        
        self.last_study_date = today
        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak
        
        self.save()
    
    def add_xp(self, amount):
        """Adiciona XP e verifica level up"""
        old_level = self.current_level
        self.total_xp += amount
        
        # Cálculo de nível baseado em XP
        # Level 1: 0-99 XP, Level 2: 100-299 XP, etc.
        new_level = min(100, max(1, (self.total_xp // 100) + 1))
        
        if new_level > old_level:
            self.current_level = new_level
            # Adicionar recompensa por level up
            self.coins += new_level * 10
            self.gems += new_level // 5
        
        self.save()
        return new_level > old_level  # Retorna True se subiu de nível


class UserProfile(models.Model):
    """Perfil estendido do usuário"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Dados sensíveis criptografados (LGPD)
    encrypted_cpf = models.TextField(blank=True, null=True)
    encrypted_phone = models.TextField(blank=True, null=True)
    
    # Preferências de estudo
    favorite_subjects = models.JSONField(default=list)
    weak_subjects = models.JSONField(default=list)
    study_goals = models.JSONField(default=dict)
    
    # Configurações de notificação
    push_notifications = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    streak_reminders = models.BooleanField(default=True)
    
    # Dados de acesso
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    login_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Perfil do Usuário'
        verbose_name_plural = 'Perfis dos Usuários'
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def encrypt_sensitive_data(self, data):
        """Criptografa dados sensíveis"""
        if not data:
            return None
        
        # Usar chave do settings ou gerar uma
        key = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Descriptografa dados sensíveis"""
        if not encrypted_data:
            return None
        
        key = getattr(settings, 'ENCRYPTION_KEY', Fernet.generate_key())
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()
    
    def set_cpf(self, cpf):
        """Define CPF criptografado"""
        self.encrypted_cpf = self.encrypt_sensitive_data(cpf)
    
    def get_cpf(self):
        """Obtém CPF descriptografado"""
        return self.decrypt_sensitive_data(self.encrypted_cpf)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Cria automaticamente o perfil do usuário quando um usuário é criado"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Salva o perfil do usuário quando o usuário é salvo"""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class UserActivity(models.Model):
    """Registro de atividades do usuário para auditoria e analytics"""
    
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('question_answered', 'Questão Respondida'),
        ('lesson_completed', 'Lição Completada'),
        ('achievement_unlocked', 'Conquista Desbloqueada'),
        ('purchase', 'Compra'),
        ('profile_updated', 'Perfil Atualizado'),
        ('password_changed', 'Senha Alterada'),
        ('data_export', 'Exportação de Dados'),
        ('data_deletion', 'Exclusão de Dados'),
        ('consent_given', 'Consentimento Concedido'),
        ('consent_withdrawn', 'Consentimento Retirado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.TextField()
    
    # Dados contextuais
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    additional_data = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Atividade do Usuário'
        verbose_name_plural = 'Atividades dos Usuários'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"


class LGPDConsent(models.Model):
    """Registro de consentimentos LGPD"""
    
    CONSENT_TYPES = [
        ('data_processing', 'Processamento de Dados'),
        ('marketing', 'Marketing'),
        ('analytics', 'Analytics'),
        ('cookies', 'Cookies'),
        ('third_party_sharing', 'Compartilhamento com Terceiros'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lgpd_consents')
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPES)
    granted = models.BooleanField()
    
    # Metadados do consentimento
    consent_text = models.TextField(default='Consentimento padrão')  # Texto exato apresentado ao usuário
    version = models.CharField(max_length=20, default='1.0')  # Versão dos termos
    ip_address = models.GenericIPAddressField(default='127.0.0.1')
    user_agent = models.TextField(default='Unknown')
    
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Consentimento LGPD'
        verbose_name_plural = 'Consentimentos LGPD'
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user', 'consent_type']),
            models.Index(fields=['granted_at']),
        ]
    
    def __str__(self):
        status = "Concedido" if self.granted else "Negado"
        return f"{self.user.username} - {self.get_consent_type_display()} ({status})"
    
    @property
    def is_expired(self):
        """Verifica se o consentimento expirou"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
