"""
Modelos para sistema de notificações
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class NotificationTemplate(models.Model):
    """Templates de notificações"""
    
    NOTIFICATION_TYPES = [
        ('study_reminder', 'Lembrete de Estudo'),
        ('achievement_unlocked', 'Conquista Desbloqueada'),
        ('streak_reminder', 'Lembrete de Sequência'),
        ('simulation_available', 'Simulado Disponível'),
        ('new_content', 'Novo Conteúdo'),
        ('subscription_expiring', 'Assinatura Expirando'),
        ('daily_goal', 'Meta Diária'),
        ('weekly_report', 'Relatório Semanal'),
        ('friend_activity', 'Atividade de Amigo'),
        ('competition_result', 'Resultado de Competição'),
    ]
    
    PLATFORMS = [
        ('web', 'Web'),
        ('mobile', 'Mobile'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    ]
    
    name = models.CharField(max_length=100)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    
    # Conteúdo da notificação
    title_template = models.CharField(max_length=200)
    body_template = models.TextField()
    action_url = models.CharField(max_length=500, blank=True)
    icon_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    
    # Configurações
    is_active = models.BooleanField(default=True)
    priority = models.CharField(max_length=10, choices=[
        ('low', 'Baixa'),
        ('normal', 'Normal'),
        ('high', 'Alta'),
        ('urgent', 'Urgente')
    ], default='normal')
    
    # Configurações de envio
    can_be_disabled = models.BooleanField(default=True)
    requires_subscription = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Template de Notificação'
        verbose_name_plural = 'Templates de Notificação'
        unique_together = ['notification_type', 'platform']
    
    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"


class UserNotificationSettings(models.Model):
    """Configurações de notificação do usuário"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Notificações gerais
    push_notifications_enabled = models.BooleanField(default=True)
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=False)
    
    # Tipos específicos
    study_reminders = models.BooleanField(default=True)
    achievement_notifications = models.BooleanField(default=True)
    streak_reminders = models.BooleanField(default=True)
    simulation_notifications = models.BooleanField(default=True)
    content_notifications = models.BooleanField(default=True)
    subscription_notifications = models.BooleanField(default=True)
    social_notifications = models.BooleanField(default=True)
    
    # Horários preferenciais
    notification_start_time = models.TimeField(default='08:00')
    notification_end_time = models.TimeField(default='22:00')
    
    # Frequência
    daily_reminder_enabled = models.BooleanField(default=True)
    weekly_report_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuração de Notificação'
        verbose_name_plural = 'Configurações de Notificação'
    
    def __str__(self):
        return f"Configurações de {self.user.email}"


class DeviceToken(models.Model):
    """Tokens de dispositivos para push notifications"""
    
    DEVICE_TYPES = [
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.TextField()  # FCM token ou similar
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPES)
    device_id = models.CharField(max_length=200, blank=True)
    
    # Metadados do dispositivo
    app_version = models.CharField(max_length=20, blank=True)
    os_version = models.CharField(max_length=20, blank=True)
    device_model = models.CharField(max_length=100, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    last_used_at = models.DateTimeField(auto_now=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Token de Dispositivo'
        verbose_name_plural = 'Tokens de Dispositivos'
        unique_together = ['user', 'token']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_device_type_display()}"


class Notification(models.Model):
    """Notificações enviadas aos usuários"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('sent', 'Enviada'),
        ('delivered', 'Entregue'),
        ('read', 'Lida'),
        ('failed', 'Falhada'),
        ('cancelled', 'Cancelada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, null=True, blank=True)
    
    # Conteúdo da notificação
    title = models.CharField(max_length=200)
    body = models.TextField()
    action_url = models.CharField(max_length=500, blank=True)
    icon_url = models.URLField(blank=True)
    image_url = models.URLField(blank=True)
    
    # Metadados
    notification_type = models.CharField(max_length=30)
    platform = models.CharField(max_length=20)
    priority = models.CharField(max_length=10, default='normal')
    
    # Status e tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
    scheduled_for = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Dados adicionais
    metadata = models.JSONField(default=dict)  # Dados específicos da notificação
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['scheduled_for']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_sent(self):
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()


class NotificationSchedule(models.Model):
    """Agendamento de notificações recorrentes"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('custom', 'Personalizado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_schedules')
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE)
    
    # Configurações de agendamento
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    time_of_day = models.TimeField()
    days_of_week = models.CharField(max_length=20, blank=True)  # JSON: [1,2,3,4,5] para seg-sex
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Controle
    last_sent_at = models.DateTimeField(null=True, blank=True)
    next_send_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Agendamento de Notificação'
        verbose_name_plural = 'Agendamentos de Notificação'
    
    def __str__(self):
        return f"{self.template.name} - {self.user.email} ({self.get_frequency_display()})"


class NotificationAnalytics(models.Model):
    """Analytics de notificações"""
    
    template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE, related_name='analytics')
    platform = models.CharField(max_length=20)
    
    # Métricas diárias
    date = models.DateField()
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_read = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    
    # Métricas calculadas
    delivery_rate = models.FloatField(default=0.0)  # delivered/sent
    open_rate = models.FloatField(default=0.0)      # read/delivered
    click_rate = models.FloatField(default=0.0)     # clicked/read
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Analytics de Notificação'
        verbose_name_plural = 'Analytics de Notificações'
        unique_together = ['template', 'platform', 'date']
    
    def __str__(self):
        return f"{self.template.name} - {self.date}"
