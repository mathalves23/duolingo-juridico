"""
Signals para integrações externas
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import ExternalContent, DataSync, APIUsageLog

User = get_user_model()

# Signals básicos para evitar erro de import
# Será expandido conforme necessário

@receiver(post_save, sender=ExternalContent)
def process_external_content(sender, instance, created, **kwargs):
    """Processa conteúdo externo quando criado"""
    if created:
        # Aqui você pode adicionar lógica para processar o conteúdo
        pass


@receiver(pre_save, sender=DataSync)
def update_sync_duration(sender, instance, **kwargs):
    """Calcula duração da sincronização"""
    if instance.status == 'completed' and instance.started_at and not instance.duration_seconds:
        instance.duration_seconds = int((timezone.now() - instance.started_at).total_seconds()) 